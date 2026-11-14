---
source_url: https://docs.litellm.ai/docs/tutorials/claude_code_skills
source_type: docs
title: "LiteLLM Skills — Manage LiteLLM with AI Agents"
author: LiteLLM
date_published: unknown
date_extracted: "2026-10-25"
last_checked: "2026-10-25"
status: current
confidence_overall: settled
issue: "#1888"
---
# LiteLLM Skills — Manage LiteLLM with AI Agents

> Agent Skills (agentskills.io) package for managing a live LiteLLM proxy via curl against admin APIs; installable and usable by agents that support the standard (Claude Code, OpenCode, OpenClaw, etc.).

## Source Context

- **Type**: docs
- **Author credibility**: LiteLLM (official documentation for the LiteLLM proxy project).
- **Scope**: Documents `litellm-skills` repo, installation, requirements, available skills grouped by resource (Users, Teams, API Keys, Organizations, Models, MCP Servers, Agents, Usage), and how the agent-driven flow works. Does not cover implementation details of the skills themselves beyond the surface operations.

## Extracted Claims

### Claim 1: litellm-skills is an Agent Skills package for live proxy management
- **Evidence**: Official docs state purpose and compatibility.
- **Confidence**: settled
- **Quote**: "litellm-skills is a collection of Agent Skills for managing a live LiteLLM proxy. Install them once and any agent that supports the Agent Skills standard (Claude Code, OpenCode, OpenClaw, etc.) can create users, teams, keys, models, MCP servers, agents, and query usage, all by running curl commands against your proxy."
- **Our assessment**: Directly matches what the issue describes; this is the concrete artifact the page provides.

### Claim 2: Installation is a single shell command pulling from the skills repo
- **Evidence**: Install section gives curl command.
- **Confidence**: settled
- **Quote**: "curl -fsSL https://raw.githubusercontent.com/BerriAI/litellm-skills/main/install.sh | sh"
- **Our assessment**: Standard install pattern; verifiable.

### Claim 3: Requirements include a running proxy and an admin key (not a virtual key scoped to llm_api_routes)
- **Evidence**: Requirements list.
- **Confidence**: settled
- **Quote**: "- `curl` installed\n- A running LiteLLM proxy (local or remote)\n- A proxy admin key, not a virtual key scoped to `llm_api_routes`"
- **Our assessment**: Important security/permission boundary for agent-driven admin operations.

### Claim 4: Skills cover CRUD and management across Users, Teams, API Keys, Organizations, Models, MCP Servers, Agents, and Usage
- **Evidence**: Tables listing skills and what they do.
- **Confidence**: settled
- **Quote**: "### Users\n\nSkill | What it does\n--- | ---\n`/add-user` | Create a user — email, role, budget, model access\n`/update-user` | Update budget, role, or models for an existing user\n`/delete-user` | Delete one or more users\n\n### Teams\n\nSkill | What it does\n--- | ---\n`/add-team` | Create a team with budget and model limits\n`/update-team` | Update budget, models, or rate limits\n`/delete-team` | Delete one or more teams\n\n### API Keys\n\nSkill | What it does\n--- | ---\n`/add-key` | Generate a key scoped to a user, team, budget, and expiry\n`/update-key` | Update budget, models, or expiry\n`/delete-key` | Delete by key value or alias\n\n### Organizations\n\nSkill | What it does\n--- | ---\n`/add-org` | Create an org with budget and model access\n`/delete-org` | Delete one or more orgs\n\n### Models\n\nSkill | What it does\n--- | ---\n`/add-model` | Add any provider (OpenAI, Azure, Anthropic, Bedrock, Ollama…) and test it\n`/update-model` | Rotate credentials or swap the underlying deployment\n`/delete-model` | Remove a model\n\n### MCP Servers\n\nSkill | What it does\n--- | ---\n`/add-mcp` | Register an MCP server (SSE, HTTP, or stdio)\n`/update-mcp` | Update URL, credentials, or allowed tools\n`/delete-mcp` | Remove an MCP server\n\n### Agents\n\nSkill | What it does\n--- | ---\n`/add-agent` | Create an agent backed by a model and optional MCP servers\n`/update-agent` | Swap the model or update description and limits\n`/delete-agent` | Remove an agent\n\n### Usage\n\nSkill | What it does\n--- | ---\n`/view-usage` | Daily spend and token activity — by user, team, org, or model"
- **Our assessment**: Comprehensive surface area for proxy administration via agent skills.

### Claim 5: The agent-driven flow prompts for config, collects required fields, runs curl, and reports results
- **Evidence**: How it works section.
- **Confidence**: settled
- **Quote**: "When you invoke a skill, the agent asks for your `LITELLM_BASE_URL` and admin key, collects the fields needed for that operation, runs the `curl`, and shows the result. For example:\n\n```\n/add-model\n```\n\n→ Agent asks: provider, public name, credentials. Adds the model, runs a test completion, reports pass/fail.\n\n```\n/view-usage\n```\n\n→ Agent asks: date range (defaults to current month), optional team/model filter. Prints a table of daily requests, tokens, and spend."
- **Our assessment**: Clear UX pattern for agent skills operating against APIs.

## Concrete Artifacts

```bash
curl -fsSL https://raw.githubusercontent.com/BerriAI/litellm-skills/main/install.sh | sh
```

Example skill invocations described:
```text
/add-model
/view-usage
```

## Cross-References

- **Corroborates**: `source-notes/docs-litellm-completion-web-search.md` (both are LiteLLM docs pages about extending/operating LiteLLM; related to LiteLLM ecosystem) — but more directly this is about admin via agents/skills.
- **Contradicts**: (none found)
- **Extends**: `source-notes/docs-litellm-batches-api.md` (LiteLLM API surface area) — complementary operational/admin surface.
- **Novel**: Introduces Agent Skills (`agentskills.io`) as a distribution/UX mechanism for LiteLLM proxy administration (installable skill set usable by Claude Code/OpenCode/OpenClaw) with concrete skill catalog and agent-driven curl flow.

## Guide Impact

- **Chapter 03 (Tooling & IDE Integration)** or **Chapter 07 (Operations/Orchestration)**: Document LiteLLM Skills as an option for managing LiteLLM proxy via agent skills (admin automation). Note requirement for admin key (not llm_api_routes-scoped virtual key) and that it uses curl against proxy APIs. Consider adding to "AI Tools" / agent tooling section as a way to manage LiteLLM with AI agents.

## Extraction Notes

- Source page was reached via redirect from `https://docs.litellm.ai/docs/manage_with_ai_agents` to `/docs/ai_tools` and the specific "Manage LiteLLM with AI Agents" item links to `/docs/tutorials/claude_code_skills`. Fetched the tutorial page directly.
- No paywall observed; content extracted verbatim as presented.
- Related notes candidates from miner-related-notes.md were reviewed; no direct claim-level citations made (different topic focus: skills/admin vs batches/web-search/evals). Treated as suggested only.
