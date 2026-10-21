---
source_url: https://docs.litellm.ai/docs/enterprise
source_type: docs
title: "LiteLLM Enterprise — LiteLLM Documentation"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; current as of 2026-10-21)
date_extracted: 2026-10-21
last_checked: 2026-10-21
status: current
confidence_overall: emerging
issue: "#1679"
---

# LiteLLM Enterprise (LiteLLM Docs)

> LiteLLM Enterprise layers SSO/SCIM, audit logs, org/team admin roles, secret managers, IP allowlists, per-team logging, multi-region, and professional support onto the same open-source Gateway image; SSO is free for up to 5 users beyond which an Enterprise license is required. Many governance features are surfaced as "Enterprise" only, while the OSS guardrail framework differs in which built-in integrations require a license.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway Enterprise page).
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation. Claims about feature gating/licensing and product surface are authoritative for the vendor's positioning; no production metrics or failure-mode analysis are provided.
- **Scope**: Covers what Enterprise adds on top of OSS Gateway/SDK (SSO/SCIM, audit logs, RBAC/orgs/teams/projects, budgets/tags/alerts, secret managers, IP allowlists, per-team logging/exports, branding/limits, support SLAs/version support), license activation, SOC 2 posture, procurement, and which guardrail callbacks require a license.

## Extracted Claims

### Claim 1: Enterprise is a license key on the same Gateway image (no migration) with layered tiers: Python SDK (OSS) → AI Gateway (OSS) → Enterprise (license)
- **Evidence**: The page shows a layered diagram stating "EnterpriseLicense key on the Gateway. Everything in AI Gateway, plus..." and "AI GatewayOpen source, self-hosted. Everything in the SDK, plus..." with bullet lists for each layer.
- **Confidence**: settled
- **Quote**: "Enterprise is a license key on the same Gateway image you may already run. Nothing to migrate: each layer includes everything below it."
- **Our assessment**: Clear positioning — it's a feature-gate on the same build, not a fork; operationally this means upgrades/version alignment between OSS and Enterprise share the same image/version line.

### Claim 2: SSO is free for up to 5 users; beyond that, an Enterprise license is required
- **Evidence**: Stated in "Who is Enterprise for?" section.
- **Confidence**: settled
- **Quote**: "SSO is free for up to 5 users; beyond that, an Enterprise license is required."
- **Our assessment**: Important boundary condition for adoption decisions (small teams can try SSO before licensing).

### Claim 3: Enterprise adds SSO/SCIM, audit logs, delegated/org/team admin roles, secret managers, IP allowlists, per-team logging, multi-region, and professional support SLAs
- **Evidence**: "What you get on top of open source" and detailed feature lists under Security/access, Governance/cost, Observability/compliance, Operations/branding.
- **Confidence**: settled
- **Quote**: "Enterprise adds SSO, audit logs, admin roles for each team, and help from the LiteLLM engineers."
- **Our assessment**: Core governance/control-plane capabilities are gated to Enterprise.

### Claim 4: Audit logs track every admin action and key-level change with retention policies; per-team logging allows routing logs to different backends and disabling logging per team (GDPR-friendly)
- **Evidence**: Observability/compliance bullets list "Audit Logs with retention policies. Track every admin action and key-level change" and "Team-Based Logging... Route each team's logs to their own Langfuse project or callback" plus "Disable logging per team".
- **Confidence**: settled
- **Quote**: "[Audit logs](/docs/proxy/audit_logs). Track every admin action and key-level change, with retention policies your compliance team sets."
- **Our assessment**: Strong compliance story; per-team log routing/disablement are relevant for multi-tenant governance.

### Claim 5: Secret managers supported (AWS KMS/Secrets Manager, Azure Key Vault, Google KMS/Secret Manager, HashiCorp Vault, CyberArk, or custom) with automatic virtual key rotation; IP allowlists restrict proxy access
- **Evidence**: Security/access bullets.
- **Confidence**: settled
- **Quote**: "[Secret managers](/docs/secret_managers/overview). AWS KMS, AWS Secrets Manager, Azure Key Vault, Google KMS, Google Secret Manager, HashiCorp Vault, CyberArk, or a custom secret manager"
- **Our assessment**: Provider-agnostic secrets integration is a notable Enterprise capability for regulated environments.

### Claim 6: Governance includes multi-tenant orgs/teams/projects/keys, project management with budgets/owners/rate limits/model allowlists/isolated spend, tag-based budgets, per-model budgets per virtual key, temporary budget increases, soft budget alerts, and spend reports
- **Evidence**: Governance and cost bullets.
- **Confidence**: settled
- **Quote**: "[Multi-tenant Architecture](/docs/proxy/multi_tenant_architecture). Organizations, teams, projects, and keys"
- **Our assessment**: Granular cost governance is heavily featured; useful for chargeback/showback patterns.

### Claim 7: SOC 2 Type II audited; self-hosted (no data leaves environment); signed Docker images; procurement via AWS/Azure Marketplace or direct
- **Evidence**: Security claims and FAQ/procurement notes.
- **Confidence**: emerging (vendor-audited; report available via Trust Center)
- **Quote**: "[SOC 2 Type II](https://trust.litellm.ai/). Audited controls; request the report through the Trust Center"
- **Our assessment**: Compliance posture is documented; verification requires Trust Center access.

### Claim 8: Support includes dedicated Slack/Teams channel with engineers; optional 24/7 SLAs with 1h for Sev 0 and 72h for security patches; version support is 4 most recent stable minor lines, OSS and Enterprise share same image/version
- **Evidence**: Support and Version support sections.
- **Confidence**: settled
- **Quote**: "Every license includes a dedicated Slack or Teams channel with the engineering team. With the optional 24/7 SLAs, the response time is 1 hour for Sev 0 and 72 hours for security patches."
- **Our assessment**: Support terms are explicit; version parity simplifies upgrades.

### Claim 9: Certain guardrails require Enterprise license (built-in callback integrations): `llmguard_moderations`, `llamaguard_moderations`, `hide_secrets`, `openai_moderations`, `google_text_moderation`, `lakera_prompt_injection`, `aporia_prompt_injection`; OSS guardrail framework includes custom guardrails and Presidio for PII masking
- **Evidence**: "Which guardrails need a license?" section.
- **Confidence**: settled
- **Quote**: "The OSS guardrail framework includes custom guardrails and Presidio for PII masking. These built-in callback integrations require a LiteLLM Enterprise license: `llmguard_moderations`, `llamaguard_moderations`, `hide_secrets`, `openai_moderations`, `google_text_moderation`, `lakera_prompt_injection`, and `aporia_prompt_injection`."
- **Our assessment**: Important gating detail — some moderation/PIN/secret-detection integrations are Enterprise-only even if guardrails framework exists in OSS.

### Claim 10: License activation is via `LITELLM_LICENSE` env var; Enterprise Edition shown on API docs page when active
- **Evidence**: Run it and FAQ sections.
- **Confidence': settled
- **Quote**: "Add the license key to your environment, then restart the proxy. LITELLM_LICENSE=\"eyJ...\". Open `http://<your-proxy-host>:<port>/`. The API docs page should show **Enterprise Edition** in the description."
- **Our assessment**: Simple activation model consistent with "license key on same image".

## Concrete Artifacts

```text
EnterpriseLicense key on the Gateway
...
AI GatewayOpen source, self-hosted
...
Python SDKOpen source library
```
(From layered feature diagram)

```env
LITELLM_LICENSE="eyJ..."
```
(License activation)

## Cross-References

- **Corroborates**: `source-notes/docs-litellm-data-security.md` (compliance/SOC2/trust center context), `source-notes/docs-litellm-security-settings.md` (security-related settings), `source-notes/docs-litellm-gateway-auth-reference.md` (auth surface)
- **Contradicts**: none obvious
- **Extends**: `source-notes/docs-litellm-a2a-agent-gateway.md` (governance applies to agents as well), `source-notes/docs-litellm-completion-input-params.md` (operational controls)
- **Novel**: Explicit license-gating matrix for specific guardrail integrations and the "SSO free up to 5 users" boundary; layered OSS/Enterprise model with same-image deployment.

## Guide Impact

- **Chapter [SRE/LLM Ops / Gateway Governance]**: When evaluating LiteLLM for multi-tenant/enterprise use, treat SSO/audit/RBAC/secret managers/IP allowlists/per-team logging as Enterprise-gated (with noted exceptions like SSO up to 5 users). Account for guardrail integration licensing when planning moderation/PII/secret-detection coverage. Note same-image/version parity simplifies upgrade paths.

## Extraction Notes

- Deep read of the full enterprise page (features, support, versioning, FAQ). Followed links conceptually via content but extracted only from this page per scope. No paywall encountered. Thin in terms of concrete config examples beyond env var, but rich in feature/licensing boundaries.
