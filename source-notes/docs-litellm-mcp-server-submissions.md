---
source_url: https://docs.litellm.ai/docs/mcp_server_submissions
source_type: docs
title: "MCP Server Submissions — LiteLLM Documentation (pending_review intake and approval gate)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; .md metadata last_updated 2026-11-06)
date_extracted: 2026-11-06
last_checked: 2026-11-06
status: current
confidence_overall: emerging
issue: "#1959"
---

# MCP Server Submissions (LiteLLM Docs)

> LiteLLM documents a maker-checker intake path for MCP servers: a team-scoped
> key submits a server to `POST /v1/mcp/server/register`, the server is
> persisted as `pending_review` and deliberately **not** loaded into the
> runtime registry, and an admin or `proxy_admin_viewer` must approve it before
> clients can reach it — while admin keys bypass the whole workflow and create
> active servers directly.

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, "MCP
  Server Submissions" page under "MCP Gateway → MCP Servers"). The page's
  markdown endpoint (`/docs/mcp_server_submissions.md`) reports
  `last_updated: "2026-11-06"`.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the documented routes, request/response shapes, role
  requirements, and state transitions. It publishes no measured adoption,
  review latency, false-approval rate, or incident data. Claims below stay at
  "the gateway documents this contract" and are graded `emerging`.
- **Scope**: Covers only the submission and approval workflow — the
  `pending_review` state, the submit endpoint, the UI review path, the admin
  API list/approve/reject endpoints, status values, and four FAQ behaviours.
  It does **not** cover per-key/team/org MCP permissions
  (`docs-litellm-mcp-control.md`), outbound MCP auth (`mcp_authentication`),
  deployment exposure (`docs-litellm-mcp-deployment.md`), guardrails, rate
  limits, or the stdio command validation patched after CVE-2026-30623
  (`failure-litellm-mcp-stdio-command-injection.md`). Those are cited only as
  cross-references.
- **Pages read**: The submissions page was read in full from the live markdown
  endpoint (204 lines, HTTP 200, no paywall). The linked MCP
  Control/Deployment pages were not re-read here; their surfaces are already
  covered by existing source notes.

## Extracted Claims

### Claim 1: New MCP servers can be submitted by team members but are held in `pending_review` and are not loaded into the registry until an admin approves them
- **Evidence**: The page opener states the workflow, and the "How It Works"
  diagram makes "NOT loaded into registry" an explicit step between submission
  and review.
- **Confidence**: emerging (documented workflow; no measured review outcomes)
- **Quote**: "LiteLLM supports a submission and approval workflow for MCP servers. Team members can submit MCP servers for admin review, and the server is held in a `pending_review` state until an admin approves or rejects it."
- **Quote**: "This lets organizations give team members self-service MCP registration without immediately exposing unapproved servers to all users."
- **Our assessment**: This is the load-bearing trust-gate claim: the control is
  at *intake*, not at request time, and it is fail-closed — the server does not
  merely get hidden from listings, it is not loaded into the runtime registry.
  It complements, rather than replaces, the request-time permission model
  (`docs-litellm-mcp-control.md` Claim 2 still documents MCP access as open by
  default when no level defines a list). Approval makes a server *registered*;
  it is not shown here to grant it to any particular key.

### Claim 2: The workflow requires `store_model_in_db: true` but has no separate feature flag
- **Evidence**: The Prerequisites list names `store_model_in_db: true` as
  required to persist MCP servers; the FAQ says the endpoints are available by
  default once that setting is present.
- **Confidence**: emerging (explicit prerequisite and default)
- **Quote**: "`store_model_in_db: true` must be set in your proxy config (required to persist MCP servers)"
- **Quote**: "No. The submission endpoints are available by default as long as `store_model_in_db: true` is set. No additional feature flags are required."
- **Our assessment**: Operationally, DB persistence is the real switch — a
  config-file-only deployment does not have an approval workflow to configure.
  The page does not document what the endpoints return if the setting is
  absent, so a runbook should verify the prerequisite rather than infer the
  failure mode.

### Claim 3: Submission is restricted to a team-scoped API key; admin keys are rejected at the submit endpoint and bypass the workflow through `POST /v1/mcp/server`
- **Evidence**: The Prerequisites bullet and the "User: Submit an MCP Server"
  section both state the same split.
- **Confidence**: emerging (explicit role boundary)
- **Quote**: "The submitting user must use a team-scoped API key (admin keys bypass the workflow and use `POST /v1/mcp/server` directly)"
- **Quote**: "Use a team-scoped API key. Admin keys are rejected at this endpoint; admins should use `POST /v1/mcp/server` directly."
- **Our assessment**: This is the sharpest limitation of the control. The gate
  constrains non-admin self-service, not admins: an admin can create an active
  server directly and never enter `pending_review`. That prevents unvetted team
  registrations but does not provide four-eyes review for admin actions or
  protect against a compromised admin key. The page documents no second
  approver and no separation-of-duties rule.

### Claim 4: The submit endpoint is `POST /v1/mcp/server/register`; its response returns a `server_id`, `pending_review` status, submitter identity, and submission timestamp, but the submitted server is not yet reachable by clients
- **Evidence**: The curl example, the JSON response block, and the note below
  it.
- **Confidence**: emerging (documented request/response contract)
- **Quote**: "The server is not accessible to MCP clients yet. It only becomes active after an admin approves it."
- **Our assessment**: `submitted_by` and `submitted_at` give the review record
  basic attribution. The documented request body carries `server_name`, `url`,
  `transport`, and `description` only — there is no structured justification or
  risk-classification field, so any "why should this be approved?" evidence
  has to live outside the workflow (description or ticket).

### Claim 5: The UI review surface is a "Submitted MCPs" tab with counters and per-submission cards; approval is a confirmation dialog that immediately loads the server into the registry, and rejection accepts optional free-text review notes
- **Evidence**: The "Admin: Review Submissions → Via UI" section.
- **Confidence**: emerging (documented UI behaviour)
- **Quote**: "Approving a server pops a confirmation dialog. Click Approve to make it active and load it into the MCP registry immediately."
- **Quote**: "Rejecting opens a dialog with an optional review notes field, where you can explain why the submission was declined:"
- **Our assessment**: The UI shows more review evidence than the list API
  (name, description, URL, transport, date), which matters for Claim 7. But the
  approval is one confirmation click by one privileged user, and the only
  rejection rationale is optional free text — the page documents no mandatory
  reason, no review checklist, and no automated scan of the submitted server's
  tool definitions before activation.

### Claim 6: API review requires an admin or `proxy_admin_viewer` role, and exposes list, approve, and reject endpoints under `/v1/mcp/server`
- **Evidence**: The "Admin: Review Submissions → Via API" section places the
  role requirement above the list/approve/reject examples.
- **Confidence**: emerging (documented role requirement; role semantics not
  defined on this page)
- **Quote**: "Admin or `proxy_admin_viewer` role required."
- **Our assessment**: The page does not distinguish a read-only reviewer from
  an approver: the same role sentence covers `GET /v1/mcp/server/submissions`
  and the `PUT .../approve` / `PUT .../reject` mutations. A role named
  "viewer" being sufficient for approval is a least-privilege question the
  guide should not assume away — verify against the deployment's actual role
  definitions before treating `proxy_admin_viewer` as safe for read-only
  review.

### Claim 7: The list-submissions response omits `url`, `transport`, and `description`, all of which appear in the submit response and the UI cards
- **Evidence**: Direct comparison of the documented JSON bodies: the submit
  response includes `server_id`, `server_name`, `url`, `transport`,
  `approval_status`, `submitted_by`, `submitted_at`; each item in
  `GET /v1/mcp/server/submissions` includes only `server_id`, `server_name`,
  `approval_status`, `submitted_by`, `submitted_at`. The UI card description
  explicitly lists name, description, URL, transport, and date.
- **Confidence**: emerging (documented response shapes; consequence is an
  inference from the shapes)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: An API-only reviewer cannot evaluate the submitted
  endpoint from the list payload — the destination URL and transport, the two
  fields most relevant to a supply-chain or egress review, are absent. That
  pushes API-based review either to the UI or to per-server lookups the page
  does not document. The submit response has the fields, but only the
  submitter sees it at submission time.

### Claim 8: Approval moves a server to `active` and loads it into the runtime registry immediately; `pending_review`, `active`, and `rejected` are the only documented status values
- **Evidence**: The approve example's prose and the "Approval Status Values"
  table.
- **Confidence**: emerging (documented state machine)
- **Quote**: "The server status changes to `active` and it is immediately loaded into the MCP runtime registry."
- **Quote**: "Approved. Loaded into the MCP registry and available to clients."
- **Our assessment**: "Available to clients" is a registry/visibility
  statement, not a permission grant; this page never mentions key, team, or org
  entitlements and links to MCP Permission Management for access control. Read
  with `docs-litellm-mcp-control.md` Claim 13 (the registry advertises URLs and
  actual access control is still enforced when a client connects), approval
  should be modelled as "the server is now eligible to be reached", while
  per-key authorization remains a separate decision.

### Claim 9: Approval is reversible and rejection doubles as immediate revocation — the approve endpoint accepts `rejected` servers too, and rejecting a previously active server evicts it from the runtime registry
- **Evidence**: The two FAQ entries on re-approval and rejecting a previously
  active server.
- **Confidence**: emerging (explicit documented FAQ behaviour)
- **Quote**: "Yes. Call `PUT /v1/mcp/server/{id}/approve`; the endpoint accepts servers in both `pending_review` and `rejected` status."
- **Quote**: "It is evicted from the runtime registry immediately, so clients will no longer see its tools."
- **Our assessment**: This is the operationally important half of the state
  machine: reject is not only an intake decision but also the documented
  revocation path for an active server. It gives operators a fast kill switch
  without deleting the server record, and rejected servers can be re-approved
  later. The page documents no approval lock, no expiry, and no audit event for
  these transitions.

### Claim 10: The page documents no timeout, expiry, notification, or review SLA for `pending_review` submissions — a submission waits until an admin acts
- **Evidence**: The status table defines `pending_review` only as "waiting for
  admin review"; neither "How It Works" nor the FAQ documents a timeout,
  notification, escalation, or automatic rejection.
- **Confidence**: emerging (absence in a living vendor page; future releases
  may add it)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The only documented observability is the UI's submission
  counters (Total Submitted, Pending Review, Active, Rejected) and the list
  API's summary fields. A growing `pending_review` queue is therefore a silent
  operational failure mode unless the operator adds an external alert on those
  counters. This is an absence claim, not evidence that a hidden timeout
  exists.

## Concrete Artifacts

### Intake state machine (verbatim from `docs/mcp_server_submissions`)

```text
Team member submits MCP server via API
        ↓
Server saved as "pending_review" (NOT loaded into registry)
        ↓
Admin reviews in the Submitted MCPs tab
        ↓
Approve → server goes "active" and is loaded into the registry
Reject  → server stays out with optional review notes
```

### Prerequisite config (verbatim from `docs/mcp_server_submissions`)

```yaml title="config.yaml"
general_settings:
  store_model_in_db: true
```

### Submit a server (verbatim from `docs/mcp_server_submissions`)

```bash
curl -X POST http://localhost:4000/v1/mcp/server/register \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TEAM_API_KEY" \
  -d '{
    "server_name": "github_mcp",
    "url": "https://api.githubcopilot.com/mcp",
    "transport": "sse",
    "description": "GitHub MCP for code search and PR management"
  }'
```

### Submission response (verbatim from `docs/mcp_server_submissions`)

```json
{
  "server_id": "832d6abc-7a5c-457a-a9f6-cfe4ae05f776",
  "server_name": "github_mcp",
  "url": "https://api.githubcopilot.com/mcp",
  "transport": "sse",
  "approval_status": "pending_review",
  "submitted_by": "7fd77c87-207b-4d6c-9d51-b72efb8962dc",
  "submitted_at": "2026-04-29T18:50:34Z"
}
```

### List submissions (verbatim from `docs/mcp_server_submissions`)

```bash
curl http://localhost:4000/v1/mcp/server/submissions \
  -H "Authorization: Bearer $ADMIN_API_KEY"
```

```json
{
  "total": 1,
  "pending_review": 1,
  "active": 0,
  "rejected": 0,
  "items": [
    {
      "server_id": "832d6abc-7a5c-457a-a9f6-cfe4ae05f776",
      "server_name": "github_mcp",
      "approval_status": "pending_review",
      "submitted_by": "7fd77c87-207b-4d6c-9d51-b72efb8962dc",
      "submitted_at": "2026-04-29T18:50:34Z"
    }
  ]
}
```

### Approve and reject (verbatim from `docs/mcp_server_submissions`)

```bash
curl -X PUT http://localhost:4000/v1/mcp/server/{server_id}/approve \
  -H "Authorization: Bearer $ADMIN_API_KEY"
```

```bash
curl -X PUT http://localhost:4000/v1/mcp/server/{server_id}/reject \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $ADMIN_API_KEY" \
  -d '{"review_notes": "This URL is not on the approved vendor list."}'
```

### Status values (verbatim from `docs/mcp_server_submissions`)

| Status | Meaning |
|--------|---------|
| `pending_review` | Submitted, waiting for admin review. Not accessible to MCP clients. |
| `active` | Approved. Loaded into the MCP registry and available to clients. |
| `rejected` | Rejected by admin. Not accessible. May include `review_notes`. |

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-mcp-control.md` **Claim 13** — both notes
    separate registry visibility from authorization. That claim says the MCP
    registry "only advertises server URLs" and that actual access control is
    still enforced when the client connects; this page's "available to clients"
    is the same registry/eligibility sense, not a per-key grant. The two pages
    cover different layers of the same separation.
  - `source-notes/docs-langfuse-halo.md` **Claim 2** — both document a human
    approval gate as the thing that stands between a proposed capability and
    its effect. The mechanisms differ (Halo pauses individual mutating tool
    calls at runtime; LiteLLM approves a server once at intake), but they
    corroborate the same posture: no unreviewed change takes effect.
- **Contradicts**: None. Two apparent tensions are scope differences, not
  contradictions, and no contradiction issue was filed:
  1. This page's "available to clients" after approval versus
     `docs-litellm-mcp-control.md` **Claim 13**'s "access control is still
     enforced." The first is a registry/eligibility statement; the second is
     the request-time authorization rule. Both can hold at once.
  2. This page's admin bypass (`POST /v1/mcp/server` creates directly) versus
     the stdio command-injection note's requirement that MCP server
     creation/testing be constrained. The first is a review-workflow role
     split; the second is input validation after CVE-2026-30623. Seen in
     Cross-References → Extends below, not as opposing claims.
- **Extends**:
  - `source-notes/docs-litellm-mcp-control.md` **Claim 2** — that note
    documents the request-time permission default (no level has a list → every
    MCP server is reachable). This page adds the missing *intake* layer: even
    after approval, the server still runs under that permission default, so the
    approval workflow does not change the open-by-default authorization
    behaviour once a server is active.
  - `source-notes/docs-litellm-mcp-deployment.md` **Claims 6–7** — that note
    documents `available_on_public_internet` defaulting to `true` and the
    caller-IP filter. This page adds an orthogonal intake control: approval
    does not set or imply the public-internet flag, so a newly approved server
    can still be externally visible by default unless the operator sets it.
    Intake review and exposure review are separate checklist items.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md`
    **"Fix Layer 1"** (the `MCP_STDIO_ALLOWED_COMMANDS` allowlist) — the
    approval workflow is a human review gate over server metadata, not an
    input-validation control. It does not replace the stdio command allowlist,
    Pydantic validation, runtime re-validation, or `PROXY_ADMIN` gating
    documented in that note. Pair the two: approval controls *whether* a
    server enters the registry; the CVE fix controls *what a server definition
    may execute*.
  - `source-notes/docs-litellm-mcp-control.md` **Claim 9** (tool pinning) and
    **Claim 8** (`allowed_params`) — these are post-approval controls. The
    submission page documents no tool-list pinning, parameter filtering, or
    automated inspection of the submitted server's tools, so approval is not a
    substitute for pinning/guardrails on an active server.
- **Novel**: No existing source note covers this surface. A grep of
  `source-notes/`, `registry/`, and `guide/` found no occurrence of
  `pending_review`, `mcp/server/register`, `mcp/server/submissions`,
  `approval_status`, or `submitted_by` outside this note. New to the corpus:
  1. The MCP server submission/approval state machine (`pending_review` →
     `active`/`rejected`) and the rule that pending servers are not loaded into
     the runtime registry.
  2. The team-scoped-key submit / admin-bypass split, and the fact that the
     gate does not apply to admin-created servers.
  3. The three review endpoints (`/register`, `/submissions`, `/{id}/approve`,
     `/{id}/reject`) and their request/response shapes.
  4. Reject-as-revocation (eviction from the runtime registry) and
     re-approval of rejected servers.
  5. The list-response information gap (`url`/`transport`/`description`
     absent) and the documented absence of timeout/notification for
     `pending_review`.

## Guide Impact

- **Chapter 06 (Security and Trust) — Trust rollout patterns**: Add an "MCP
  server intake approval" pattern beside the existing shadow → suggest → act
  material: self-service submission by a team-scoped key, `pending_review`
  state that is not loaded into the registry, one-click admin approval or
  rejection with optional notes, and reject-as-revocation for active servers
  (Claims 1, 5, 8, 9). State the limitation explicitly: admin keys bypass the
  workflow, so this is an intake control for non-admin self-service, not
  four-eyes review of privileged administrators (Claim 3). If the guide wants
  separation of duties for admin-created MCP servers, it must recommend an
  additional control the vendor page does not provide.
- **Chapter 06 (Security and Trust) — MCP hardening**: Position the approval
  gate as necessary but insufficient. It reviews metadata (name, description,
  URL, transport) and does not validate the server definition, scan tool
  descriptions, pin the tool list, or substitute for the stdio command
  allowlist after CVE-2026-30623 (Claims 4–5; Cross-References to
  `failure-litellm-mcp-stdio-command-injection.md` and
  `docs-litellm-mcp-control.md` Claim 9). Approving a server should be
  followed by the existing pinning/parameter/guardrail controls before clients
  rely on it.
- **Chapter 05 (LLM Ops Reliability) — gateway config and runbooks**: Add the
  MCP submission workflow to the gateway production checklist: set
  `store_model_in_db: true` before promising self-service registration (Claim
  2), issue team-scoped keys for submitters (Claim 3), and define who holds
  admin/`proxy_admin_viewer` because that role set is documented as sufficient
  for approve/reject (Claim 6). Add an alert on the `pending_review` counter
  and a review SLA, since the page documents no timeout, notification, or
  escalation (Claim 10). For API-driven review, note that the list payload
  omits URL/transport/description, so the runbook must fetch or display the
  full submission before approval (Claim 7).
- **Chapter 05 (LLM Ops Reliability) — config-change release gating**: The
  approve/reject state transitions are a registry change that takes effect
  immediately (Claims 8–9). Treat an approval as a config change with the same
  three-property test the chapter already applies: know how to roll it back
  (reject evicts an active server), and verify that client-facing tool lists
  actually drop the tools when a server is rejected.

## Extraction Notes

- Read the live markdown endpoint
  (`https://docs.litellm.ai/docs/mcp_server_submissions.md`) in full (204
  lines, HTTP 200, no paywall). No sub-pages were followed: the page is short
  and self-contained, and the linked MCP Control/Deployment material is already
  covered by existing source notes.
- Quotes were copied from the markdown source. Where the source uses bold
  emphasis inside a sentence, the quote carries the rendered sentence with the
  markdown emphasis markers removed; inline code spans are preserved. No quote
  splices non-adjacent sentences. Claims 7 and 10 have no direct quote because
  their evidence is, respectively, a comparison of two JSON shapes and an
  absence in the page; both are labelled accordingly.
- Candidate-list dispositions (from `miner-related-notes.md`):
  - `docs-litellm-batches-api.md` — batch rate limiting, unrelated to MCP
    server intake.
  - `docs-litellm-mcp-deployment.md` — **cited** (Claims 6–7) for the
    orthogonal public-internet exposure default.
  - `docs-litellm-mcp-zero-trust.md` — outbound MCP JWT signing, unrelated to
    the submission workflow.
  - `docs-litellm-evals-api.md` — Evaluations API, unrelated.
  - `docs-litellm-completion-web-search.md` — provider web search, unrelated.
  - `docs-litellm-generate-content.md` — Google `generateContent`
    passthrough, unrelated.
  - `docs-litellm-enterprise.md` — licensing/feature gating, no submission or
    approval content.
  - `docs-litellm-mcp-aws-sigv4.md` — SigV4 outbound auth, unrelated.
  - `docs-litellm-mcp-oauth-passthrough.md` — OAuth token passthrough, a
    different MCP auth surface; not cited because it does not address intake or
    approval.
  - `docs-litellm-completion-input-params.md` — completion parameter gate,
    unrelated.
- Additional cross-references beyond the candidate list were found by searching
  `source-notes/`: `docs-litellm-mcp-control.md`,
  `docs-litellm-mcp-deployment.md`, `failure-litellm-mcp-stdio-command-injection.md`,
  and `docs-langfuse-halo.md`. Each cited claim was re-read and verified in the
  cited note before writing (MINER.md §4b).
- `last_updated: "2026-11-06"` matches the extraction date, so no staleness
  caveat beyond the living-page caveat. The page documents no notification,
  timeout, or audit-event surface for submissions; this is recorded as an
  absence claim (Claim 10), not as a hidden feature.
- No contradiction issue was filed. The apparent "available to clients" versus
  "access control still enforced" tension is a registry-versus-authorization
  scope difference, not a materially opposing claim.
