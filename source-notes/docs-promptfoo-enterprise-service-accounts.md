---
source_url: https://www.promptfoo.dev/docs/enterprise/service-accounts
source_type: docs
title: "Promptfoo Enterprise: Service Accounts — Inert-by-Default Credential Scoping, Display-Once Keys, and the Unbounded Global-Admin Flag"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-15
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: settled
issue: "#1625"
---

# Promptfoo Enterprise: Service Accounts

> Machine identities in Promptfoo Enterprise follow an "inert-until-bound" scoping contract: a service account API key has no programmatic access until it is assigned to a team with a role, and the key is displayed exactly once at creation.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise "Enterprise > Service Accounts" page). The page carries the gating notice "This feature requires Promptfoo Enterprise." Footer: "Last updated on **Oct 15, 2026** by **renovate[bot]**" (dependency bump).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor, documenting its own Enterprise control plane. The procedural steps and credential properties are string-checkable against the page.
- **Scope**: Covers creating and managing service accounts for programmatic access (CI/CD, automated testing). Documents: creation path via Organization Settings → Users → "Create Service Account"; the key is shown once only; optional global-admin privilege granting "everything that can be done in the organization settings page"; and mandatory team+role assignment (an unassigned key has no programmatic access).
- **Not covered**: CLI/API schemas or endpoints, header format, token prefix, key rotation/expiry/revocation procedures, scope granularity beyond team+role, rate limits/quotas, environment variable handling, or secret-manager integration. No concrete code/config examples beyond the UI flow.

## Extracted Claims

### Claim 1: Creation is a privileged operation — only global system admins can create and assign service accounts
- **Evidence**: The callout note at the top of the page states creation authority explicitly.
- **Confidence**: settled
- **Quote**: "Only global system admins can create and assign service accounts."
- **Our assessment**: Buy this. The credential-issuing path is an admin surface, not self-service. This matches the authority boundary described elsewhere in Enterprise docs.

### Claim 2: A service account API key is displayed exactly once at creation and cannot be retrieved later
- **Evidence**: After creation, the page shows the key in a dialog and warns it cannot be viewed again after closing.
- **Confidence**: settled
- **Quote**: "Make sure to copy your API key when it's first created. For security reasons, you won't be able to view it again after closing the dialog."
- **Our assessment**: Buy this. The lifecycle consequence is clear: loss of the key requires creating a new service account (minting a replacement). The page offers no documented rotation/revocation/expiry path to mitigate this.

### Claim 3: The key is inert by default — service account API keys have no programmatic access until assigned to a team and role
- **Evidence**: The final step explicitly states the scoping requirement as a gating condition on programmatic access.
- **Confidence**: settled
- **Quote**: "Service account API keys will not have programmatic access to Promptfoo Enterprise unless assigned to a team and role."
- **Our assessment**: Buy this. The credential follows an "inert until bound" contract — scoping is mandatory, not optional. An unbound key is not a weaker credential; it is effectively non-functional for programmatic use. This is the key operational pattern for least-privilege scoping of machine identities.

### Claim 4: A service account may be granted global admin privileges, which unboundedly cover organization settings
- **Evidence**: Step 4 describes the optional global admin toggle and enumerates the surfaces it covers.
- **Confidence**: settled
- **Quote**: "Determine if you want to assign the API key with global admin privileges. This will provision the API key with access to everything that can be done in the organization settings page, such as managing teams, roles, users, and webhooks."
- **Our assessment**: Buy this. Granting global admin to a machine identity (especially for CI/CD) is a high-privilege escalation path. The "everything that can be done in the organization settings page" scope is unbounded relative to a specific workload — teams, roles, users, and webhooks are all administrative surfaces. This creates an org takeover risk if such a token is leaked.

### Claim 5: The documented credential lifecycle omits rotation, expiry, revocation, and retrieval procedures (absence set)
- **Evidence**: The page describes creation, display-once, optional global admin, and team+role assignment. It contains no guidance on key rotation, expiration, revocation flows, token format, endpoints, CLI usage, or secret management integration.
- **Confidence**: settled (absence is directly observable on this page)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The page names CI/CD pipelines as the use case but documents none of the operational controls typically expected for standing CI credentials (rotation policy, expiry, revocation procedure, scope enumeration beyond team+role). This absence is operationally meaningful — the documented contract is create-and-store-once with no recovery path.

## Concrete Artifacts

### Creation flow (verbatim summary from steps)
```
1. Navigate to Organization Settings → Users → Create Service Account
2. Enter name; save API key in secure location (shown once; cannot be re-viewed)
3. Optionally assign global admin (org settings: teams, roles, users, webhooks)
4. Assign to a team via Teams → Service Accounts section with a predefined role
5. Without team assignment, key has no programmatic access
```

*(Attribution: promptfoo docs "Enterprise > Service Accounts".)*

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 8** — already quotes this page's scoping/authority statements verbatim ("Only global system admins can create and assign service accounts", "will not have programmatic access ... unless assigned to a team and role", the global-admin scope over org settings). (Verified by re-reading that note's quoted material.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 3** — notes `service_account_created` and `service_account_deleted` are the only service-account events in the audit taxonomy, with no rotation/re-issue event. This aligns with Claim 5 above (lifecycle gaps).
  - `source-notes/docs-promptfoo-enterprise-authentication.md` — establishes the Enterprise auth context (SSO/OIDC/SAML, CLI login flow). While not duplicating service-account details, it situates machine identity alongside human identity in the Enterprise surface.

- **Contradicts**: None identified. The material is consistent with the audit-logging note's prior coverage.

- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` — builds on its existing cross-read by adding a first-class treatment of: (a) the display-once/non-retrievable property as an operational constraint, (b) the inert-by-default "unassigned = no access" contract as a concrete scoping pattern, (c) the explicit absence set (rotation/expiry/revocation/token mechanics) stated as absence rather than inference. These are deltas not fully elaborated in the audit-logging note.

- **Novel**: While three sentences from this page already appear quoted in `docs-promptfoo-enterprise-audit-logging.md`, this source note provides a focused, structured extraction specific to the service account credential model (Claims 2-5, concrete artifact flow) with lifecycle absences called out explicitly. This is the first dedicated source note for this URL.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Reinforces the "Gateway credential routing: declare, don't infer" principle. The inert-until-bound behavior (Claim 3) is a concrete instantiation — credentials must be explicitly scoped to a team+role; unbound keys must not be treated as valid. Also highlights the escalation risk of granting global admin to CI-held machine identities (Claim 4).
- **Chapter 05 (LLM Ops Reliability)**: For CI/CD pipelines that gate evals, the display-once property (Claim 2) combined with no documented rotation/expiry/revocation (Claim 5) means pipelines must treat service account keys as high-impact secrets requiring external rotation/escrow. The absence set should be captured when evaluating platform suitability for automated gating.

## Extraction Notes

- Read the full page via direct fetch (https://www.promptfoo.dev/docs/enterprise/service-accounts). The content is a short procedural doc (6 numbered steps + callouts). No sub-pages followed beyond the page itself; the "See Also" links (`teams`, `authentication`) were read for context only.
- Cross-referenced against existing notes: confirmed overlap with `docs-promptfoo-enterprise-audit-logging.md` Claim 8 (verbatim quotes already exist there). Per triage guidance, this note extends rather than duplicates.
- No contradiction issue filed; the material is consistent with existing corpus.
- `miner-related-notes.md` candidates: the top candidates included audit-logging (score 0.2292), which is cited as Corroborates/Extends. Other candidates were dismissed as unrelated (batches, findings, guardrails, etc.) — not about service accounts.
- Registry files (`registry/sources.json`, `registry/claims-index.json`) were not edited (derived indexes).
