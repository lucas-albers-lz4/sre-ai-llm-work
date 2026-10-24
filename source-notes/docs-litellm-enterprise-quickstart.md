---
source_url: https://docs.litellm.ai/docs/learn/enterprise_quickstart
source_type: docs
title: "Enterprise Quickstart — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs)
date_extracted: 2026-10-24
last_checked: 2026-10-24
status: current
confidence_overall: emerging
issue: "#1855"
---

# LiteLLM Enterprise Quickstart (Rollout Runbook)

> Ordered rollout procedure for LiteLLM Enterprise (deploy → configure access for models/MCP/agents → test calls → secure auth → chargeback). Treats several deployment/auth/chargeback choices as constraints to set correctly at go-live and gives verification checks for enforcement (budget/rate-limit errors).

## Source Context

- **Type**: docs (official vendor runbook — LiteLLM Enterprise quickstart).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Authoritative for stated configuration ordering and verification steps; no production metrics or failure analysis provided.
- **Scope**: Step-by-step deployment (Docker Compose / raw K8s manifests / Helm chart), adding models/MCP servers/agents and granting team access, making sample LLM/MCP/agent calls, implementing SSO/JWT/least privilege/secret manager/audit logs, and setting up chargeback (org/team/user/key/projects/tags) with budget/rate-limit/tag-budget verification. Skips marketing/pricing details.

## Extracted Claims

### Claim 1: Deployment supports three paths with Postgres required as system of record for keys/budgets/registries; Redis 7.0+ is required when running more than one instance or worker (each instance enforces independently otherwise)
- **Evidence**: Prerequisites/deployment tabs (Docker Compose, raw manifests, Helm). Docker Compose example uses `postgres` service and `DATABASE_URL` pointing to Postgres; raw manifests require existing Postgres reachable from cluster; Helm can provision Postgres (`db.deployStandalone: true`) or use existing DB. The page states "Redis 7.0+" as a prerequisite in the context of scaling across instances/workers (implied by scaling concerns) and the Prospector triage explicitly calls this out as correctness issue when multi-instance. The quickstart emphasizes Postgres as store (`store_model_in_db: true` in examples).
- **Confidence**: emerging
- **Quote**: (no direct single-line quote captured in visible text; see Our assessment)
- **Our assessment**: The quickstart's deployment shapes all require Postgres configuration; operational scaling note (Redis for shared enforcement across instances/workers) is flagged by triage as a decision-shaped constraint even if not loudly called out in every snippet — treat as vendor-stated correctness constraint for multi-replica deployments.

### Claim 2: Critical deployment settings include `LITELLM_MASTER_KEY` (from env/secret), `LITELLM_SALT_KEY` set before first model and never rotated (encrypts stored provider credentials), license via `LITELLM_LICENSE`, and `store_model_in_db: true` in general settings
- **Evidence**: Raw manifest Secret example creates `litellm-secrets` with `LITELLM_MASTER_KEY`, `LITELLM_SALT_KEY`, `LITELLM_LICENSE`, `OPENAI_API_KEY`, `DATABASE_URL`. ConfigMap shows `general_settings.master_key: os.environ/LITELLM_MASTER_KEY` and `store_model_in_db: true`. Helm values pass master key and license via secrets/env.
- **Confidence**: settled
- **Quote**: "kubectl create secret generic litellm-secrets \\\n  --from-literal=LITELLM_MASTER_KEY=\"sk-<paste-a-long-random-key>\" \\\n  --from-literal=LITELLM_SALT_KEY=\"sk-salt-change-me\" \\\n  --from-literal=LITELLM_LICENSE=\"eyJ...\" \\\n  --from-literal=OPENAI_API_KEY=\"your-api-key\" \\\n  --from-literal=DATABASE_URL=\"postgresql://user:pass@host:5432/litellm\""
- **Our assessment**: Ordering/immutability of salt key is called out by triage as hard-to-change after go-live; quickstart shows setting it at deploy time alongside master key and license.

### Claim 3: Rollout sequence builds tenancy first (Organization → Team → Internal Users → team `max_budget` → team virtual key), then attaches MCP/agents, then tests calls, then tightens auth
- **Evidence**: Step 2 table: create org and team, invite internal users (gateway tracks spend per user), set team `max_budget` (e.g. $10/30d), create team virtual key with access to model. Step 2c adds MCP tools (allow in MCP settings for team/key), Step 2d adds agents (deploy sample agent, allow in agent settings of virtual key).
- **Confidence**: settled
- **Quote**: "| Step | Action | Why |\n|---|---|---|\n| 1 | Create an **Organization** and a **Team** | An organization is the top-level entity... An organization contains teams... |\n| 2 | Invite **Internal Users** to the team | Each user gets access to the team models, and the gateway tracks the spend of each user. |\n| 3 | Set the team **`max_budget`** (for example `$10` for `30d`) | The budget gives a hard spend limit. In Step 5, you use it to examine budget enforcement. |\n| 4 | Create a **team virtual key** with access to the model | Applications use this key in Step 3. The gateway records the spend of the key and the team. |"
- **Our assessment**: Explicit ordered sequence with rationale; aligns with chargeback hierarchy described later.

### Claim 4: Same virtual key and same budgets apply to LLM, MCP, and agent requests (unified budget across modalities)
- **Evidence**: Step 5 states "The same virtual key and the same budgets apply to LLM, MCP, and agent requests." Verification step 5a says after step 3 make sure spend includes LLM, MCP, and agent calls.
- **Confidence**: settled
- **Quote**: "The same virtual key and the same budgets apply to LLM, MCP, and agent requests."
- **Our assessment**: Strong unification claim; matches triage's question about single budget across LLM/MCP/A2A.

### Claim 5: Auth hardening path — sign in with master key initially, configure SSO (register redirect URI `https://<base>/sso/callback`), then disable master-key and `UI_PASSWORD` login; workloads can use JWT from OIDC mapped to user/team/model access; use service accounts per workload, least-privilege RBAC, IP filtering; keep provider keys in secret manager
- **Evidence**: Step 4 describes SSO setup with provider-specific env vars and redirect URI, then disable environment credential login; JWT auth for API traffic via claims mapping; least privilege (small proxy admins, service account keys per workload, IP filtering); secret manager for provider keys.
- **Confidence**: settled
- **Quote**: "SSO controls the login to the Admin UI. API requests use a different method: virtual keys or JWT. Register this redirect URI in your identity provider:\n\n```\nhttps://<your-proxy-base-url>/sso/callback\n```"
- **Our assessment**: Clear transition from bootstrap auth to production auth with explicit disable step.

### Claim 6: Audit logs are on by default when licensed; can opt out with `store_audit_logs: false` in `litellm_settings`; test by deleting a key and checking Audit Logs page
- **Evidence**: Step 4 audit logs section states default-on with license, opt-out flag, and test procedure.
- **Confidence**: settled
- **Quote**: "Audit logs are on by default when the gateway has a license. To turn them off, set `store_audit_logs: false` in `litellm_settings`. To do a test, delete a virtual key in the API or the Admin UI. Then open the **Audit Logs** page. Refer to [Audit logs](/docs/proxy/audit_logs)."
- **Our assessment**: Explicit default-on behavior relevant to compliance posture.

### Claim 7: Chargeback hierarchy is org → team → user → virtual key with projects and tags as additional dimensions; enforcement verified by deliberately setting low budgets/rate limits and asserting errors (team budget $0.0001 → budget error; key with `rpm_limit: 1` → rate limit error on second request in minute; tag budget with tiny limit → budget error on second tagged request)
- **Evidence**: Step 5 describes attribution levels and dimensions; 5a tests team budget by setting very low value and expecting budget error; 5c creates key with `max_budget: 0.01, rpm_limit: 1` and expects 200 on first, rate limit error on second in same minute; 5d configures `tag_budget_config` with tiny budget and expects budget error on second tagged request.
- **Confidence**: settled
- **Quote**: "- Optional: set the team `max_budget` to a very low value, for example `$0.0001`. Send one LLM request, and make sure that the gateway returns a budget error.\n- Create a key with a small budget and an RPM limit: ... `\"max_budget\": 0.01, \"rpm_limit\": 1, ...` ... Send a request with the new key. Make sure that the response is `200 OK`. Send a second request in the same minute. Make sure that the gateway returns a rate limit error.\n- Add `tag_budget_config` to `config.yaml` ... `poc:chat-app: max_budget: 0.000000000001, budget_duration: 1d` ... Make sure that the first request is successful. Send a second request with the same tag. Make sure that the gateway returns a budget error."
- **Our assessment**: Runbook treats enforcement verification as required step (acceptance checks), not optional — useful operational guidance.

### Claim 8: Model names in examples are illustrative (e.g. `gpt-6.1-sol`) and image/chart references move over time; verify Enterprise Edition shows on API docs page after activation
- **Evidence**: Examples use `gpt-6.1-sol` throughout; deployment uses `docker.litellm.ai/berriai/litellm:latest` and OCI Helm chart; triage notes to treat model IDs as illustrative/as-of date.
- **Confidence**: settled
- **Quote**: "- model_name: gpt-6.1-sol\n          litellm_params:\n            model: openai/gpt-6.1-sol"
- **Our assessment**: Good to note as provenance caveat for reproducibility.

## Concrete Artifacts

```yaml
# ConfigMap snippet (raw manifests) showing critical settings
general_settings:
  master_key: os.environ/LITELLM_MASTER_KEY
  database_url: "postgresql://llmproxy:dbpassword9090@db:5432/litellm"
  store_model_in_db: true
```

```bash
# Secret creation (raw manifests)
kubectl create secret generic litellm-secrets \
  --from-literal=LITELLM_MASTER_KEY="sk-<paste-a-long-random-key>" \
  --from-literal=LITELLM_SALT_KEY="sk-salt-change-me" \
  --from-literal=LITELLM_LICENSE="eyJ..." \
  --from-literal=OPENAI_API_KEY="your-api-key" \
  --from-literal=DATABASE_URL="postgresql://user:pass@host:5432/litellm"
```

```text
SSO redirect URI:
https://<your-proxy-base-url>/sso/callback
```

```bash
# Key with budget and rate limit
curl -X POST 'http://localhost:4000/key/generate' \
  -H "Authorization: Bearer $LITELLM_API_KEY" \
  -H 'Content-Type: application/json' \
  -d '{
    "max_budget": 0.01,
    "rpm_limit": 1,
    "team_id": "<your-team-id>"
  }'
```

```yaml
# Tag budget config
litellm_settings:
  tag_budget_config:
    poc:chat-app:
      max_budget: 0.000000000001
      budget_duration: 1d
```

```python
# A2A agent call (example)
LITELLM_BASE_URL = "http://localhost:4000"
LITELLM_VIRTUAL_KEY = "sk-team-key"
# ... uses a2a.client to call agent via gateway
```

## Cross-References

- **Corroborates**: `source-notes/docs-litellm-enterprise.md` (Enterprise feature surface/licensing; this quickstart is the procedural rollout counterpart extending it), `source-notes/docs-litellm-gateway-auth-reference.md` (auth/key mechanics), `source-notes/docs-litellm-a2a-cost-tracking.md` / `source-notes/docs-litellm-a2a-invoking-agents.md` (agent cost attribution and invocation), `source-notes/docs-litellm-data-security.md` (salt/master key/secret handling context)
- **Contradicts**: none obvious
- **Extends**: `source-notes/docs-litellm-enterprise.md` (adds ordered rollout steps, concrete verification checks for budget/rate limits, unified LLM/MCP/A2A budget enforcement, default-on audit logs with test procedure, SSO/JWT transition steps)
- **Novel**: Concrete go-live acceptance checks (deliberately trigger budget/rate-limit/tag-budget errors), explicit unified budget across LLM/MCP/A2A, ordered tenancy setup with verification, default-on audit logs with opt-out and test procedure

## Guide Impact

- **`guide/05-llm-ops-reliability.md`**: Add operational checklist for LiteLLM Enterprise rollout — Postgres required (system of record), Redis 7.0+ required for multi-instance/worker shared enforcement (correctness, not perf), `LITELLM_SALT_KEY` set before first model and immutable, master key in secret manager, `store_model_in_db: true`. Include verification steps (budget/rate-limit/tag-budget error cases) as acceptance criteria. Note same budgets apply to LLM/MCP/agent traffic.
- **`guide/06-security-and-trust.md`**: Document auth transition (bootstrap master key → SSO for Admin UI with redirect URI `.../sso/callback`, disable master-key/UI_PASSWORD login), JWT for API traffic mapped to user/team/model, service accounts per workload, least-privilege RBAC, IP filtering, secret manager for provider keys, audit logs default-on with license (opt-out `store_audit_logs: false`) and verification procedure.
- **`guide/03-runbooks-and-agents.md`**: Capture ordered tenancy sequence (org→team→users→team budget→team virtual key), MCP/agent attachment and permissioning, unified cost attribution across LLM/MCP/A2A, and chargeback dimensions (org/team/user/key/project/tags).

## Extraction Notes

- Deep read of the full quickstart page (all deployment tabs, all steps 1-5, auth, chargeback, after-rollout). Focused on decision-shaped/procedural claims per triage guidance; skipped duplicating raw YAML/Helm boilerplate except concrete critical snippets. Treated `gpt-6.1-sol` and image tags as illustrative/as-of retrieval date. No paywall encountered.
- Cross-referenced against existing `docs-litellm-enterprise.md` — quickstart is procedural counterpart (extends rather than duplicates). Relied on triage's explicit callouts (salt immutability, Redis multi-instance correctness, unified budget across modalities) while extracting verifiable steps from the page.
