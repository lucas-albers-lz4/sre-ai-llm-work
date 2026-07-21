---
source_url: https://docs.litellm.ai/blog/google-ai-studio-managed-agents
source_type: blog-post
title: "Google AI Studio Managed Agents on LiteLLM"
author: "Sameer Kankute (SWE @ LiteLLM), Krrish Dholakia (CEO, LiteLLM), Ishaan Jaffer (CTO, LiteLLM)"
date_published: 2026-05-19
date_extracted: 2026-07-21
last_checked: 2026-07-21
status: current
confidence_overall: settled
issue: "#398"
---

# Google AI Studio Managed Agents on LiteLLM

> A feature-announcement / integration guide from LiteLLM engineers documenting how
> LiteLLM v1.87.0 proxies Google AI Studio's Managed Agents API, providing auth
> relay, CRUD agent lifecycle management, and interaction routing through the LiteLLM
> gateway — with documented limitations and configuration examples.

## Source Context

- **Type**: blog-post (feature announcement / how-to integration guide)
- **Author credibility**: Written by LiteLLM engineers (Sameer Kankute, SWE; Krrish
  Dholakia, CEO; Ishaan Jaffer, CTO) — the people building and maintaining the
  integration. High credibility for *what the integration does and how to configure it*
  (it is their own documentation), lower for general claims about managed-agent
  patterns beyond this specific integration.
- **Scope**: Covers (1) proxy configuration for managed-agent API routing (env vars,
  auth relay, version requirements), (2) agent CRUD lifecycle through LiteLLM's
  `/v1beta/agents` proxy endpoint (create, list, get, delete, version listing),
  (3) agent interaction routing via `/v1beta/interactions`, (4) auth model
  (GEMINI_API_KEY delegation through proxy vs SDK direct), (5) documented limitations.
  Does NOT cover: performance metrics, failure scenarios, comparative analysis with
  other provider integrations, or production operational experience.

## Extracted Claims

### Claim 1: LiteLLM v1.87.0+ proxies Google AI Studio's Managed Agents API through its gateway, providing OpenAI-compatible CRUD endpoints for agent lifecycle management
- **Evidence**: Full code examples showing both curl (proxy) and Python SDK usage for
  create, list, get, delete, and version-listing of agents. Version requirement stated
  explicitly in a callout box.
- **Confidence**: settled
- **Quote**: "LiteLLM now supports the Google AI Studio Managed Agents API, allowing
  users to 'Create, manage, and run custom agents through LiteLLM.'"
- **Quote**: "Available from LiteLLM v1.87.0-dev.1 or above."
- **Our assessment**: This is a documented, shipped feature at a specific version.
  The claim is fully evidenced by the code examples throughout the post. Treat as
  settled fact.

### Claim 2: LiteLLM acts purely as an auth + routing pass-through layer — agents live entirely on Google's side and are not persisted in LiteLLM's database
- **Evidence**: Stated explicitly in the Overview section. The consequence is also
  documented: deleting an agent via Google's API directly leaves the proxy unaware.
- **Confidence**: settled
- **Quote**: "LiteLLM does 'not' store the agent in its own database. The agent lives
  entirely on Google's side. LiteLLM is 'just the auth + routing layer.'"
- **Our assessment**: A straightforward architectural claim about LiteLLM's design
  choice. This has real operational implications: agents managed through LiteLLM
  have an out-of-band state risk (deletion through Google's API creates a cache
  inconsistency). The proxy has no recovery mechanism for this — a noteworthy
  limitation for production deployments.

### Claim 3: Managed agents require GEMINI_API_KEY in the proxy environment; there is no per-request API key mechanism at the proxy endpoint
- **Evidence**: Auth table in the post explicitly maps proxy auth to
  GEMINI_API_KEY/GOOGLE_API_KEY env vars, and notes the proxy does not support
  per-request `api_key` parameter.
- **Confidence**: settled
- **Quote**: "GEMINI_API_KEY / GOOGLE_API_KEY must be present in the proxy environment.
  Passing the key per-request via api_key is supported in the SDK but not currently
  via the proxy endpoint."
- **Our assessment**: This creates a multi-tenant operational constraint: the proxy's
  Gemini managed-agent capability is tied to a single GEMINI_API_KEY at the proxy
  level. Virtual keys (`sk-...`) authenticate users to the proxy, but the proxy
  always uses the same downstream Google key. Tenant-level key management (per-customer
  Gemini keys) is not supported through the proxy endpoint pattern.

### Claim 4: Only `antigravity-preview-05-2026` is accepted as `base_agent` — an unspecified Google-side restriction
- **Evidence**: Stated as the first limitation in the Limitations list, and noted in
  the create-agent parameters table.
- **Confidence**: settled
- **Quote**: "base_agent only accepts 'antigravity-preview-05-2026' (Google's current
  restriction)."
- **Our assessment**: This is a documented restriction from Google's API, not a
  LiteLLM limitation. It means LiteLLM's managed-agent proxy is tied to the
  availability of Google's preview model. If Google deprecates or replaces
  `antigravity-preview-05-2026`, LiteLLM will need to update to track it. For
  practitioners, this is a supply-chain dependency on Google's preview API stability.

### Claim 5: The Interactions API routes to managed agents via the `agent` field (not `model`), and this agent-specific routing is only supported for Gemini
- **Evidence**: Explicitly documented with code examples; the note on the agent-vs-model
  distinction is highlighted. The limitation is stated in the Limitations section.
- **Confidence**: settled
- **Quote**: "Note: pass agent, not model. The agent name is not a LiteLLM model; do
  not put it in the model field."
- **Quote**: "Using the Interactions API via the agent param is only supported by
  Gemini as of now. Use the model param to call other providers' models."
- **Our assessment**: This is a critical architectural detail for the guide's gateway
  material: the proxy introduces a new routing dimension — `agent` — that is
  semantically different from the existing `model` field. `agent` routes to a
  managed, stateful entity (the custom agent on Google's side); `model` routes to a
  stateless model endpoint. This dual-routing pattern (model calls vs agent
  interactions) is a first concrete example of the "gateway routing agent work"
  pattern from LiteLLM's strategy post.

### Claim 6: Creating an agent with a duplicate name returns a 409 Conflict from Google — there is no upsert or update-by-create pattern
- **Evidence**: Noted in the create-agent section's parameters table as a side-effect
  of Google's API behavior.
- **Confidence**: settled
- **Quote**: "Calling create twice with the same name returns a 409 Conflict from
  Google."
- **Our assessment**: A documented API constraint from Google's Managed Agents API.
  This means the standard create-or-update idempotency pattern (PUT) is unavailable;
  users must handle 409s explicitly. LiteLLM does not paper over this — the raw
  Google error surfaces through the proxy to the caller.

### Claim 7: Agent deletion through Google's API directly creates a cache inconsistency — the LiteLLM proxy will not know the agent was deleted
- **Evidence**: Stated explicitly in the Limitations section.
- **Confidence**: settled
- **Quote**: "Agents are stored on Google's side only. LiteLLM does not persist them
  in its database. If you delete an agent via Google's API directly, the proxy will
  not know."
- **Our assessment**: This is a state-management gap in the pass-through architecture.
  If a user or automated process deletes an agent through Google's console or API
  (bypassing LiteLLM), subsequent interaction attempts through LiteLLM will fail with
  an unclear error (Google will reject the request for a nonexistent agent). The proxy
  provides no reconciliation mechanism. This is a real operational concern for teams
  that manage agents through multiple interfaces.

## Concrete Artifacts

### Proxy configuration (verbatim from article)

```yaml
general_settings:
  master_key: "sk-1234"
environment_variables:
  GEMINI_API_KEY: "AIzaSy..."   # or set in shell env
```

### Create agent — curl (proxy) example (verbatim)

```bash
curl -X POST "http://localhost:4000/v1beta/agents" \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-custom-slides-agent",
    "base_agent": "antigravity-preview-05-2026",
    "instructions": "You are a helpful assistant that creates slides.",
    "base_environment": {"env_id": "YOUR_ENVIRONMENT_ID"}
  }'
```

### Create agent — Python SDK example (verbatim)

```python
response = litellm.interactions.agents.create(
    name="my-slides-agent",
    base_agent="antigravity-preview-05-2026",
    instructions="You are a helpful assistant that creates slides.",
    custom_llm_provider="gemini",
    base_environment={"env_id": "YOUR_ENVIRONMENT_ID"})
print(response.id)  # "my-slides-agent"
```

### Run an agent — proxy (verbatim)

```bash
curl -X POST "http://localhost:4000/v1beta/interactions" \
  -H "Authorization: Bearer sk-1234" \
  -H "Content-Type: application/json" \
  -d '{
    "agent": "my-slides-agent",
    "input": "Create a slide deck on the Fibonacci sequence",
    "environment": "remote"
  }'
```

### Run an agent — SDK (verbatim)

```python
response = litellm.interactions.create(
    agent="my-slides-agent",
    input="Create a slide deck on the Fibonacci sequence",
    environment="remote")
print(response)
```

### List agents — proxy (verbatim)

```bash
curl "http://localhost:4000/v1beta/agents" \
  -H "Authorization: Bearer sk-1234"
```

Response:

```json
{
    "agents": [
        {"id": "my-custom-slides-agent"},
        {"id": "my-custom-slides-agent-1"}
    ]
}
```

### Get agent — proxy (verbatim)

```bash
curl "http://localhost:4000/v1beta/agents/my-slides-agent" \
  -H "Authorization: Bearer sk-1234"
```

Response:

```json
{
    "id": "my-custom-slides-agent",
    "base_agent": "antigravity-preview-05-2026",
    "system_instruction": "You are a helpful assistant that creates slides.",
    "base_environment": {
        "sources": [{
            "type": "gcs",
            "source": "gs://eap-templates/slides-skill",
            "target": "/.agents/skills/slides-skill"
        }],
        "type": "remote"
    }
}
```

### Delete agent — proxy (verbatim)

```bash
curl -X DELETE "http://localhost:4000/v1beta/agents/my-slides-agent" \
  -H "Authorization: Bearer sk-1234"
```

### Version-listing endpoint — proxy (verbatim)

```bash
curl "http://localhost:4000/v1beta/agents/my-slides-agent/versions" \
  -H "Authorization: Bearer sk-1234"
```

### Authentication modes (verbatim from article's auth table)

| Method | How to provide the key |
|---|---|
| **Proxy** | Set `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the proxy's environment. Virtual keys (`sk-...`) authenticate users _to the proxy_; the proxy uses your Gemini key to talk to Google. |
| **SDK** | Set `GEMINI_API_KEY` in the environment, or pass `api_key="AIzaSy..."` to each call. |

### Documented limitations (verbatim)

> * `base_agent` only accepts `"antigravity-preview-05-2026"` (Google's current restriction).
> * Agents are stored on Google's side only. LiteLLM does not persist them in its database. If you delete an agent via Google's API directly, the proxy will not know.
> * Using the Interactions API via the `agent` param is only supported by Gemini as of now. Use the `model` param to call other providers' models.
> * `GEMINI_API_KEY` / `GOOGLE_API_KEY` must be present in the proxy environment. Passing the key per-request via `api_key` is supported in the SDK but not currently via the proxy endpoint.

## Cross-References

- **Corroborates**:
  - `blog-litellm-agents-are-the-new-llms.md` (Claim 3 — a registry alone is insufficient, the hard problem is invocation across heterogeneous runtime APIs; Claim 6 — the gateway is shifting from routing model calls to routing agent work). This Managed Agents integration provides a concrete, shipped instance of both claims: the agent is created and invoked through LiteLLM's proxy as a distinct `agent`-routed primitive, separate from model calls, demonstrating the gateway's expansion beyond pure model-call routing.

- **Contradicts**: None. Verified against all existing source notes. The LiteLLM strategy note (`blog-litellm-agents-are-the-new-llms.md`) describes a broader, pre-v0 control-plane vision (LAP) that is complementary to this shipped pass-through proxy integration — they describe different product initiatives at different maturity levels. No contradiction issue filed.

- **Extends**:
  - `blog-litellm-agents-are-the-new-llms.md` — That strategy note describes LiteLLM Agent Platform (LAP) as pre-v0/experimental and the "one API across agent runtimes" as an open gap (Claim 8). This note documents a *shipped*, production-grade integration of a narrower version of the same pattern: LiteLLM proxies a single provider's managed-agent API (Google AI Studio) with concrete CRUD endpoints and interaction routing. It is a first-step implementation of the broader control-plane vision, limited to one provider and restricted to a pass-through proxy pattern (no multi-runtime orchestration, no stateful session management).
  - `blog-litellm-april-townhall-updates.md` — That townhall's roadmap signals about agent governance, MCP auth hardening, and Skills as a first-class governed primitive (Claims 11-13) are the operational support layer for the kind of integrations this Managed Agents proxy provides.

- **Novel**: First source note documenting LiteLLM's integration with a specific provider's managed-agent CRUD API. First concrete code/config examples of agent lifecycle management through an LLM gateway. First documentation of the `agent`-vs-`model` dual-routing pattern in gateway endpoints. First documented limitations list for gateway-managed-agent patterns (agent state inconsistency across proxy/provider, single-key multi-tenancy constraint, preview-model-only base_agent). The pass-through proxy pattern (LiteLLM does not own agent state) is a novel "thin gateway" architectural template not previously captured in the corpus.

## Guide Impact

- **Chapter 02 (LLM Gateway / Proxy patterns)**:
  - Add the `agent`-vs-`model` dual-routing pattern as a concrete example of the gateway's scope expanding beyond model calls to agent interactions. The proxy now has two semantically different routing dimensions: `model` routes to stateless model endpoints, `agent` routes to stateful managed agents.
  - Add the proxy-configuration pattern for managed-agent API auth relay (GEMINI_API_KEY environment variable, virtual-key user auth → downstream Google key). Note the single-key constraint: tenant-level key separation is not supported through the proxy endpoint.
  - Document the pass-through proxy architectural pattern as a distinct deployment choice: LiteLLM proxies a managed-agent API without owning agent state, creating an out-of-band state inconsistency risk.

- **Chapter 04 (Agent Infrastructure / Deployment)**:
  - Add the agent CRUD lifecycle through a gateway as a deployment pattern: agents created and managed through LiteLLM's proxy can be listed, versioned, and interacted with through a single API, but state lives on the provider side.
  - Include the 409 Conflict constraint (no upsert) and the preview-model-only base_agent constraint as operational limitations practitioners must handle when using managed agents through a gateway.
  - The version-listing capability (`/v1beta/agents/{name}/versions`) is a useful pattern for tracking agent iteration history through the gateway.

- **Chapter 05 (LLM Ops Reliability)**:
  - Add the state-inconsistency risk between proxy-managed and provider-directly-managed agents as a failure scenario: if an agent is deleted directly through Google's API, subsequent interactions through LiteLLM will fail with no proxy-side error recovery.
  - The single GEMINI_API_KEY constraint is a multi-tenancy limitation relevant to gateway capacity planning and tenant isolation.

## Extraction Notes

- Source read in full via WebFetch. The page is a rendered Docusaurus blog post
  (published May 19, 2026) on docs.litellm.ai. All quoted passages were copied
  character-for-character from the fetched markdown output and verified against the
  source URL.
- The page is self-contained with all code examples, configuration snippets, and
  documentation in a single article. No sub-pages were needed (the "See also:
  /interactions" link points to general LiteLLM interactions documentation, not
  ancillary content for this specific integration).
- `confidence_overall` set to `settled`: this is a shipped, versioned feature
  announcement with concrete, verifiable code examples and configuration
  documentation. The claims are about what the integration does, how to use it,
  and its documented limitations — not predictions or vendor forecasts.
- No contradiction issue filed: verified against all existing source notes; the
  LiteLLM strategy note describes a broader, pre-v0 control-plane vision (LAP) that
  is complementary to this shipped pass-through proxy integration — they describe
  different product initiatives at different maturity levels (pre-v0 experiment vs.
  shipped feature).
