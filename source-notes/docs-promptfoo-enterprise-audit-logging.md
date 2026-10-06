---
source_url: https://www.promptfoo.dev/docs/enterprise/audit-logging
source_type: docs
title: "Promptfoo Enterprise: Audit Logging — The Control-Plane Audit Taxonomy, Record Schema, and Pull-Only Retrieval API"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-05
date_extracted: 2026-10-05
last_checked: 2026-10-05
status: current
confidence_overall: emerging
issue: "#1589"
---

# Promptfoo Enterprise: Audit Logging

> The vendor's own account of what an eval-platform control plane records for
> audit purposes, and — more usefully for the guide — of what it does not: a
> closed taxonomy of 15 control-plane action identifiers over 5 target types
> with **zero** read/access events, a 13-field JSON record with new-state-only
> `metadata` and no source-IP attribution, and a single pull-only endpoint
> (`GET /api/v1/audit-logs`, `limit` 1–100 default 20) that is the *only*
> documented retrieval path — no retention window, no export, no webhook
> delivery, and no failed-login event.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Audit Logging" page). Page header carries the gating notice "This
  feature requires Promptfoo Enterprise." Page footer: "Last updated on **Oct 5,
  2026** by **renovate\[bot\]**" (a dependency bump, not an editorial change).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of its own Enterprise control plane, so
  authoritative *as a specification* — the action identifiers, field names,
  query-parameter names, and bounds below are the vendor's own contract and are
  string-checkable by anyone with an Enterprise tenant. It is not measurement:
  the page publishes no volume, latency, delivery-guarantee, retention, or
  cost figure, and nothing in it is verifiable in the open-source repository
  (see Extraction Notes). Page frontmatter description: "Track administrative
  operations in Promptfoo Enterprise with comprehensive audit logs for
  security, compliance, and forensic analysis."
- **Scope**: Covers what Audit Logging is for, the supported event taxonomy, the
  JSON record format and target types, three worked example entries, the
  retrieval endpoint with its seven query parameters and auth requirement, a
  four-bullet compliance-usage list, and a three-step troubleshooting list.
  Does **not** cover the data-plane tracking it defers to, any retention or
  export story, webhook delivery of audit events, alerting on privileged
  actions, the RBAC role that satisfies "Organization administrator
  privileges", or any measurement of the log's behavior under load.
- **Relationship to sibling pages**: this is the corpus's **first** coverage of a
  control-plane audit trail in an eval platform. The Enterprise pages it
  depends on — `authentication`, `service-accounts`, `teams`, `webhooks` — are
  read here only where they change what this page's claims mean (privilege
  vocabulary, the retrieval credential, and the absence of an audit sink). Two of
  them have their own open issues (#1590 authentication, and the
  configuration-telemetry question in #1561), so nothing here pre-empts those.

## Extracted Claims

### Claim 1: The feature's stated purpose is *forensic access information* answering "who, when, and what" — but the event taxonomy it then documents contains no access event, so the framing and the schema disagree about what is being logged
- **Evidence**: Opening paragraph's framing sentence plus the complete "Admin
  Operation events" list, which is 15 action identifiers: `login`,
  `user_added`, `user_removed`, `role_created`, `role_updated`, `role_deleted`,
  `team_created`, `team_deleted`, `user_added_to_team`,
  `user_removed_from_team`, `user_role_changed_in_team`, `org_admin_added`,
  `org_admin_removed`, `service_account_created`, `service_account_deleted`.
  Fourteen are administrative mutations; the fifteenth is a login. The five
  documented target types (`USER`, `ROLE`, `TEAM`, `SERVICE_ACCOUNT`,
  `ORGANIZATION`) contain nothing that represents reading or running anything.
- **Confidence**: settled (the framing sentence and the enumerated taxonomy are
  both on the page; the disagreement between them is our reading, not the
  vendor's)
- **Quote**: "Audit Logging is a feature of Promptfoo Enterprise that provides forensic access information at the organization level, user level, team level, and service account level." / "Audit Logging answers "who, when, and what" questions about promptfoo resources. These answers can help you evaluate the security of your organization, and they can provide information that you need to satisfy audit and compliance requirements."
- **Our assessment**: This is the page's most important property and the reason it belongs in the guide, so do not buy the framing. The only access-shaped event is `login`, and it is bounded to *successful* authentication (Claim 4); everything else is a change to the org's own IAM objects. So the log answers "who changed the users, teams, roles, and service accounts, and who signed in" — it does not answer "who read a configuration, who viewed a result, who ran a scan against a production target". For an eval/red-team platform the second question is the one that matters, because the workload *is* the product: a red-team scan pointed at a production endpoint, or an eval whose assertions were edited, is precisely the act a compliance reviewer wants attributed. The page's own scope note hands that class of event to an unnamed "tracked separately" surface (Claim 2), and the "Compliance Usage" section then claims HIPAA and data-protection value on the strength of "access" (Claim 10). Per MINER.md §4a this material self-disagreement is filed as
  [#1597](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1597); **no
  verdict is picked here.** The guide-side rule that is safe under either
  reading: treat this artifact as evidence of *administrative change*, not of
  *access*, and say so explicitly wherever it is cited.

### Claim 2: The coverage boundary is drawn explicitly and in control-plane vocabulary: administrative actions are logged, while "Evaluation runs, prompt testing, and other data plane operations are tracked separately" — with no named destination
- **Evidence**: The "Which events are supported by Audit Logging?" section: two
  sentences, the second of which is the boundary. The word "control plane" and
  "data plane" appear nowhere else in the Enterprise docs surface, and the
  sentence names no other product, page, or API.
- **Confidence**: settled (the boundary is stated verbatim on the page)
- **Quote**: "Audit Logging captures administrative operations within the promptfoo platform. The system tracks changes to users, teams, roles, permissions, and service accounts within your organization." / "Please note that Audit Logging captures operations in the promptfoo control plane and administrative actions. Evaluation runs, prompt testing, and other data plane operations are tracked separately."
- **Our assessment**: Buy it, and make it the reusable architectural point:
  **audit coverage of the control plane is not audit coverage of the
  workload.** Most platforms with a "who did what" log draw that line silently,
  so a reader assumes the trail covers what the product does. Promptfoo draws it
  explicitly, which is better practice than the alternative — a vendor that
  declares its boundary can be checked against it, and a vendor that does not
  cannot. What the page does *not* do is resolve the other half. "Tracked
  separately" is a deferral, not a pointer: the Enterprise webhook surface
  documents five red-team `issue.*` event types and no audit-log event (see
  Concrete Artifacts), so the red-team *findings* pipeline is visible while the
  data-plane run trail is not. For the guide, the actionable form is a test:
  before citing any product's audit log, ask whether the act you need attributed
  is in the plane the log covers, and treat "tracked separately" with no linked
  artifact as *not documented* rather than *covered*.

### Claim 3: The event taxonomy is a closed, finite list of 15 action identifiers in six categories — and every one of them is an IAM mutation except successful login, so no eval-, scan-, config-, or credential-rotation activity is auditable
- **Evidence**: The "Admin Operation events" section is presented as exhaustive
  ("The following list specifies the supported events and their corresponding
  actions:") and is grouped as Authentication (1), User Management (2), Role
  Management (3), Team Management (5), Permission Management (2), Service
  Account Management (2) — 15 in total. Cross-read against
  `site/docs/enterprise/teams.md`, whose permission list includes "Manage
  Configurations" and "Manage Targets" as governed resources: neither has a
  corresponding action.
- **Confidence**: settled (enumerated vendor contract)
- **Quote**: "The following list specifies the supported events and their corresponding actions:" / "System Admin Added: `org_admin_added` - Records when system admin permissions are granted" / "Service Account Created: `service_account_created` - Tracks creation of API service accounts"
- **Our assessment**: Buy the enumeration — a closed list is the most useful
  thing on this page, because a compliance reviewer can check it rather than
  trust it. The absence that matters for an eval platform is **not** the login
  but the missing config/target/credential events: promptfoo's RBAC layer grants
  permission to create, edit, and delete configurations and targets (teams page:
  "Manage Targets: Create, edit, and delete targets"), and those are exactly the
  objects a release gate's verdict is derived from. So the documented trail can
  tell you *who was made an admin* but not *who edited the assertion that passed
  the gate*. Two more absences with operational teeth: there is no event for
  **key rotation or re-issue** of a service-account credential — only
  `service_account_created` and `service_account_deleted` — so the credential
  provisioning timeline an incident responder needs has holes at exactly the
  point where a key was rotated rather than replaced (see **Corroborates**:
  `failure-litellm-guardrail-logging-secret-exposure.md` Lesson 4); and there is
  no event for **permission *use*** — an admin reading another team's results is
  not an administrative change, so it produces no record. The guide rule to
  state: enumerate the resources your gate's verdict depends on, then require
  each one to appear in the vendor's audit taxonomy. If it does not, the gate's
  provenance is unaudited no matter how good the IAM log is.

### Claim 4: `login` is documented as recording *successful* authentication only, so failed authentication attempts are outside the documented event set
- **Evidence**: The Authentication bullet's own wording is the bound — "Tracks
  when users successfully authenticate to the platform". No other bullet in the
  taxonomy concerns authentication, and the page's scope note does not carve out
  an exception.
- **Confidence**: settled (documented bound)
- **Quote**: "User Login: `login` - Tracks when users successfully authenticate to the platform"
- **Our assessment**: Buy it, and read it as the inversion that makes this log
  weak for its own stated purpose. An authentication audit trail exists to answer
  "was this sign-in legitimate" — and that question is answered by the *failures*,
  not the successes. With only successful logins recorded, the log cannot support
  brute-force detection, credential-stuffing correlation, or "this user was never
  supposed to be on this host", because the attempts that would show it are
  absent. The gap is wider than one event: the Enterprise authentication
  surface is much richer than one event — `site/docs/enterprise/authentication.md`
  documents basic auth plus SSO via SAML 2.0 and OIDC, a magic-link login, and a
  CLI login flow — and none of those paths' events appear in the taxonomy. So
  the log records *that a session was established*, not *how it was
  authenticated*, which is the field an auditor asks about for SSO enforcement.
  Guide line worth carrying: an audit log with only successful-auth events is
  evidence of access, never evidence of authentication correctness.

### Claim 5: The record schema is a fixed 13-field object that denormalizes actor identity into three parallel fields and carries **no source-IP, user-agent, request-id, or session attribution of any kind**
- **Evidence**: The "Audit Log format" block enumerates exactly 13 fields:
  `id`, `description`, `actorId`, `actorName`, `actorEmail`, `action`,
  `actionDisplayName`, `target`, `targetId`, `metadata`, `organizationId`,
  `teamId`, `createdAt`. Every one of the three worked examples populates the
  same 13 keys with no additional field.
- **Confidence**: settled (documented schema, and every example confirms it)
- **Quote**: "The audit log entries are stored in JSON format with the following structure:" / "\"actorId\": \"ID of the user who performed the action\"," / "\"actorEmail\": \"Email of the user who performed the action\","
- **Our assessment**: Buy the schema; draw two conclusions the page does not.
  First, **no network attribution**. Every record says *who* and *when* but not
  *from where*, so an admin action executed with a stolen token from an
  unrecognized address produces a record byte-identical in shape to a legitimate
  one. That is a real forensic ceiling: the trail can prove an identity was used,
  never that the *session* was that identity's. Any guide claim of the form "the
  audit log shows who did it" needs the qualifier "by API token, from
  unspecified origin". Second, **identity is stored three times denormalized**
  (`actorId` / `actorName` / `actorEmail`), which is the right call for
  human-readable compliance reports and simultaneously means every row is a
  PII-bearing record. That matters because the documented way to get the data out
  is to copy it somewhere else (Claim 8): pulling this feed into a third-party
  sink is an egress decision carrying an email address per row, and it deserves
  the same minimization review Ch06 already applies to guardrail payloads (see
  **Extends**).

### Claim 6: `metadata` is documented as free-form context and is `null` in two of the three worked examples; the one populated example carries the **new** permission set under an `input` key and no prior state — so the documented schema cannot answer "what did this actor remove?"
- **Evidence**: User Login example: `"metadata": null`. Team Creation example:
  `"metadata": null`. Role Update example: a nested `input` object with
  `permissions` and `description`. These are the only three payloads the page
  publishes, and the schema comment is the only statement of what `metadata` may
  contain.
- **Confidence**: emerging (the null-vs-populated pattern and the new-state-only
  shape are directly observable; whether other actions populate `metadata` is
  *not* documented — see Claim 9)
- **Quote**: "\"metadata\": null" / "\"permissions\": [\"read\", \"write\"],"
- **Our assessment**: Buy the observation, with the caveat stated in the
  confidence field. The load-bearing point is that the key is `input`: the
  documented payload is the *request* that produced the change, not a before/after
  diff. A compliance reviewer asking "this role had `delete` and now it does not
  — who removed it and when" cannot answer it from `metadata.input`; they must
  correlate the `role_updated` record against a prior snapshot of the role, which
  is to say against a state the audit log does not keep. That is a structural
  gap, not a payload gap, and it directly undercuts the page's own SOC 2 claim
  of "administrative change tracking" (Claim 10). The schema comment says
  metadata is "Additional context-specific information" with no per-action
  contract, so a consumer cannot even know whether to expect a payload. Practical
  rule for the guide: treat an audit log as *change-notification* rather than
  *change-record* unless the vendor documents a before/after pair per event type,
  and if you need diffs, capture the resource state yourself on the same poll
  cycle.

### Claim 7: Retrieval is one pull endpoint with seven query parameters and a hard page ceiling — `limit` 1–100, default 20 — with no documented sort order, so complete-trail collection is a polling loop whose pagination correctness is the consumer's problem
- **Evidence**: The "Accessing Audit Logs" section: endpoint, seven parameter
  bullets with their bounds, and the response envelope
  `{total, limit, offset, logs}`. The parameter list contains no `sort`,
  `order`, `cursor`, `after`, or `before`, and no section states an ordering
  guarantee.
- **Confidence**: settled (documented contract; the *absence* of an ordering
  guarantee is an absence, stated as such per this corpus's convention)
- **Quote**: "GET /api/v1/audit-logs" / "`limit` (optional): Number of logs to return (1-100, default: 20)" / "`offset` (optional): Number of logs to skip for pagination (default: 0)" / "`createdAtGte` (optional): Filter logs created after this ISO timestamp"
- **Our assessment**: Buy the contract, and flag the pagination hazard as the
  one thing an operator must design around. Offset pagination over an event
  stream that is *always* appending, with no documented ordering, is the classic
  skip/duplicate failure: any record landing at the head between fetching page
  *N* and page *N+1* shifts the window, so the consumer silently drops one
  record and reads another twice. The page's own parameter set contains the
  correct tool for this — `createdAtLte` plus `createdAtGte` let a collector pin
  a closed window — but `createdAt` is second-precision ISO with no tiebreaker
  field exposed for same-second records, so the safe shape is: poll a window
  closed at `createdAtLte = now - safety_margin`, dedupe on `id`, and advance
  from the maximum `createdAt` observed rather than from `offset`. Never walk
  `offset` across a live tail. Also note the practical cost of the 100-record
  ceiling: a busy organization doing routine IAM changes needs a collection job
  that runs frequently enough that 100 records is never the high-water mark,
  because there is no documented bulk-export or webhook alternative (Claim 8).
  And because the only documented retrieval path is an authenticated API call
  (Claim 8), "we'll just read it out of the UI" is not a fallback for a
  compliance archive.

### Claim 8: Reading the trail requires an organization-administrator bearer token, and the page routes the reader to Service Accounts to mint it — so the audit feed is machine-readable only through a top-tier admin credential, with no documented read-only scope
- **Evidence**: The "Authentication" subsection under "Accessing Audit Logs"
  lists two requirements; the "See Also" section's first bullet is the credential
  pointer. Cross-read `site/docs/enterprise/service-accounts.md`: "Only global
  system admins can create and assign service accounts." and "Service account
  API keys will not have programmatic access to Promptfoo Enterprise unless
  assigned to a team and role." and, for a global-admin key, access to
  "everything that can be done in the organization settings page".
- **Confidence**: settled (both requirement bullets and the See Also pointer are
  on this page; the credential-model detail is from the sibling page and is
  attributed in Concrete Artifacts)
- **Quote**: "Valid authentication token" / "Organization administrator privileges" / "Service Accounts - Create API tokens for accessing audit logs"
- **Our assessment**: Buy the requirement, and treat the composition as the
  finding. Three problems compound. (1) **The audit feed is an admin
  capability, not a read capability.** Whoever polls it holds a credential whose
  documented scope is organization-administration, i.e. the ability to change
  the very IAM objects the log records. A compliance collector is therefore a
  standing admin credential by necessity, with no documented read-only scope to
  narrow it. (2) **The vocabulary does not resolve.** This page says
  "Organization administrator"; the service-accounts page says "global admin"
  and "global system admin"; the teams page defines a permission literally named
  "Administrator: Full access to everything in the team" — a *team*-scoped
  grant. Three vocabularies, no mapping, and the page's only guidance is the
  troubleshooting step "Verify you have organization administrator privileges."
  Whether a team Administrator can read an org-wide trail is undocumented, and
  an operator hitting a 403 has no documented way to tell a permission problem
  from a malformed query. (3) **There is a bootstrap ordering problem.** Per the
  service-accounts page only global system admins can mint these keys, and
  minting one is itself an audited event (`service_account_created`) — so the
  credential that reads the audit trail is a privileged act recorded inside the
  trail it will later be used to read. That is correct behavior and worth
  stating as a pattern: an audit system whose own access events are auditable is
  the goal state, and the guide should check for it explicitly.

### Claim 9: The page defers "complete API documentation" to an API Reference that carries no retrievable specification — so the documented contract is exactly what is on this page, and everything else is unknown rather than absent
- **Evidence**: The "Accessing Audit Logs" lead sentence defers to
  `/docs/api-reference/#tag/audit-logs`. Fetching that page returns no content
  body (client-rendered spec); the repository contains no
  `site/docs/api-reference` file at the referenced paths, and a code search for
  `audit-logs` across `promptfoo/promptfoo` returns exactly one hit — this
  page's own markdown.
- **Confidence**: settled (the deferral sentence is on the page; the reference
  being unretrievable is our verification, recorded in Extraction Notes)
- **Quote**: "Audit logs are accessible through the promptfoo API. For complete API documentation, see the API Reference."
- **Our assessment**: Buy it as a documentation-coverage statement with a direct
  consequence for how the guide cites this source: **every claim in this note
  comes from this page, and anything not on this page is unknown.** That
  includes the response error shape, rate limits on the endpoint, ordering,
  maximum queryable history, whether `limit`/`offset` beyond the visible window
  is an error, and whether any `metadata` keys other than `input` exist. Do not
  let the guide state these as absent — state them as undocumented. For an
  Enterprise-gated, closed-source control plane this is the normal state of
  vendor documentation, and the guide's general rule should be the one this page
  demonstrates: **the documented surface is the auditable surface, and a
  reference you cannot fetch cannot be cited.**

### Claim 10: The compliance section names four regimes with no stated mechanism — and maps two of them to access coverage the taxonomy does not provide
- **Evidence**: The "Compliance Usage" section is four bullets, each naming a
  regime and a benefit, with no field, event, or retention statement in any of
  them. Compare the taxonomy (Claims 3–4) and the record schema (Claim 5).
- **Confidence**: anecdotal as a compliance claim (four asserted benefits, no
  mechanism, no artifact a reviewer could test); settled as a description of
  what the page asserts
- **Quote**: "**SOC 2**: Provides detailed access logs and administrative change tracking" / "**ISO 27001**: Supports access control monitoring and change management requirements" / "**Data protection reviews**: Helps track data access and user management activities" / "**HIPAA**: Provides audit trails for access to systems containing protected health information"
- **Our assessment**: Do not buy it as compliance evidence, and say why in the
  guide rather than dropping the citation silently. Three problems, in
  increasing severity. (a) "Detailed access logs" describes access logs; the
  taxonomy has no access events (Claim 1). (b) "Administrative change tracking"
  is true but weaker than it sounds: without before/after payloads
  (`metadata` is `input`-only, Claim 6) a reviewer learns *that* a role changed,
  not *what was revoked*. (c) The page supplies none of the three properties an
  auditor actually asks for: **no retention window, no export/immutability
  path, and no review cadence or alerting** on privileged grants — so a
  HIPAA-style "audit trail" claim cannot be substantiated from this page as
  documented. The four regimes are also a marketing-shaped list: they name
  frameworks without mapping any control to any field. This is filed as
  [#1597](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1597) for
  resolution; the guide-safe formulation is: **a vendor's compliance bullet is a
  claim about the vendor's program, not a specification of the artifact — look
  for the retention window, the export path, and the event taxonomy, and if all
  three are missing, the artifact evidences administrative change only.**

### Claim 11: The declared target taxonomy is wider than the action taxonomy — `ORGANIZATION` is a documented, filterable target type with no documented action that produces it, and configuration/plugin/target changes are auditable nowhere
- **Evidence**: "Audit Log Targets" lists five types; `target` is a documented
  query parameter; the 15-action list (Claim 3) contains no action documented to
  emit `ORGANIZATION`, and none covering configurations, plugins, or targets —
  all three of which the Enterprise RBAC layer treats as governed resources
  (`site/docs/enterprise/teams.md`: "Manage Configurations: Create, edit, and
  delete configurations and plugin collections"; "Manage Targets: Create, edit,
  and delete targets").
- **Confidence**: settled (both lists are enumerated on their pages; the
  mismatch is directly observable, and is an absence-of-producer claim, not a
  claim about runtime behavior)
- **Quote**: "`ORGANIZATION` - Organization-level settings" / "Manage Targets: Create, edit, and delete targets"
- **Our assessment**: Buy it, and note the shape of the gap: a documented filter
  with no documented producer. An operator or SIEM query filtering
  `?target=ORGANIZATION` is doing exactly what the docs tell them to do and will
  find nothing, with no error to distinguish "no such events" from "no events
  exist". The two `org_admin_*` actions are the closest candidates and the page
  does not state their `target`, so even the obvious mapping is undocumented. The
  larger consequence is the RBAC mismatch: promptfoo's permission model
  explicitly governs configurations, plugin collections, and targets — the
  objects that define what gets scanned and what passes — and none of them has an
  audit action. So the control plane logs *who administers the administrators*
  while remaining silent on *who administers the tests*. For an eval vendor that
  is the more consequential half, and for the guide it is the concrete form of
  "control-plane auditability is not workload auditability" (Claim 2): state the
  rule as *for each governed resource, name the audit event; if there is none,
  the resource is ungoverned*.

### Claim 12: Every worked example is illustrative rather than observed — the three `id` values are sequential suffixes on the RFC 4122 canonical example UUID and the `createdAt` values are three minutes on one afternoon in 2023
- **Evidence**: All three example `id` values are
  `550e8400-e29b-41d4-a716-446655440000` / `...0001` / `...0002` — the RFC 4122
  §3 example UUID with the last block incremented — and the three timestamps
  are `2023-11-08T08:06:40Z`, `2023-11-08T09:15:22Z`, `2023-11-08T10:30:15Z`.
  The `actorEmail`/`actorName` pairs are `john.doe@example.com`,
  `jane.smith@example.com`, `admin@example.com`.
- **Confidence**: settled (the values are on the page)
- **Quote**: "\"id\": \"550e8400-e29b-41d4-a716-446655440000\"," / "\"createdAt\": \"2023-11-08T08:06:40Z\""
- **Our assessment**: Buy it as provenance calibration, and use it to set the
  confidence split this note carries throughout. Nothing on this page is a
  measurement or a captured sample: the only payloads that exist are hand-written
  illustrations. Three consequences. (1) The `metadata` finding in Claim 6 may be
  an artifact of illustration — real `role_updated` records may carry a richer
  payload — so Claims 6 and 9 must travel together, and the guide must not assert
  "promptfoo logs no prior state", only "no prior state is documented". (2) The
  `"metadata": null` in two of three examples is *weak* evidence that `metadata`
  is usually empty, since illustrators reach for `null` to mean "nothing
  interesting here". (3) Nothing here constrains performance, volume, or delivery
  behavior at all. The practical calibration for the guide: treat the **taxonomy,
  field names, and parameter bounds** as `settled` (they are the vendor's own
  contract, string-checkable against a live Enterprise tenant) and treat
  everything about **runtime behavior** as undocumented — this is why
  `confidence_overall` is `emerging`.

### Claim 13: Retrieval has no documented failure surface — troubleshooting is three precondition checks with no error code, status, or symptom — so an empty result is ambiguous between "no activity" and "wrong query"
- **Evidence**: The "Troubleshooting" section is three numbered preconditions
  plus a support-escalation sentence. The response envelope publishes `total`
  alongside `logs`, and the parameter list includes two ISO-timestamp filters.
- **Confidence**: settled (the three items and the envelope are on the page; the
  operational consequence of their combination is our derivation)
- **Quote**: "Verify you have organization administrator privileges" / "Check that your API token is valid and has not expired" / "Ensure your query parameters are properly formatted"
- **Our assessment**: Buy the list, and extract the rule it forces. The three
  documented causes of failure are permission, credential, and query format —
  all three of which present to the caller as an empty or short page rather than
  as distinct signals, because no status code or error shape is documented. The
  dangerous case is the silent one: a `createdAtGte`/`createdAtLte` window with a
  timezone mistake or an off-by-one returns **zero rows and no error**, and "no
  audit activity occurred" is exactly the conclusion a compliance collector
  should never draw from an unvalidated query. The documented defence is in the
  envelope: read **`total`, not `logs.length`**, before concluding anything about
  activity — `total` is the only published signal that distinguishes "the window
  matched nothing" from "the window was wrong", and a sane collector asserts on
  it (query a known-good trailing window; if `total` is 0, the query is broken,
  not the org). Second rule: always pass explicit UTC ISO timestamps with a `Z`
  suffix rather than local-time strings. Third: keep the escalation path in mind
  — the documented remedy for a real problem is "contact the promptfoo support
  team", i.e. the audit surface has no self-service diagnosis, which for a
  compliance dependency is worth stating plainly in the guide.

## Concrete Artifacts

### Complete event taxonomy (verbatim from "Admin Operation events")

Six categories, 15 action identifiers. Reproduced exactly as the page lists them:

- **Authentication**
  - **User Login**: `login` - Tracks when users successfully authenticate to the platform
- **User Management**
  - **User Added**: `user_added` - Records when new users are invited or added to the organization
  - **User Removed**: `user_removed` - Logs when users are removed from the organization
- **Role Management**
  - **Role Created**: `role_created` - Captures creation of new custom roles
  - **Role Updated**: `role_updated` - Records changes to existing role permissions
  - **Role Deleted**: `role_deleted` - Logs deletion of custom roles
- **Team Management**
  - **Team Created**: `team_created` - Records creation of new teams
  - **Team Deleted**: `team_deleted` - Logs team deletion
  - **User Added to Team**: `user_added_to_team` - Tracks when users join teams
  - **User Removed from Team**: `user_removed_from_team` - Records when users leave teams
  - **User Role Changed in Team**: `user_role_changed_in_team` - Logs role changes within teams
- **Permission Management**
  - **System Admin Added**: `org_admin_added` - Records when system admin permissions are granted
  - **System Admin Removed**: `org_admin_removed` - Logs when system admin permissions are revoked
- **Service Account Management**
  - **Service Account Created**: `service_account_created` - Tracks creation of API service accounts
  - **Service Account Deleted**: `service_account_deleted` - Records deletion of service accounts

*(Attribution: promptfoo docs "Enterprise > Audit Logging > Admin Operation
events".)*

### Record schema (verbatim from "Audit Log format")

```json
{
  "id": "unique-log-entry-id",
  "description": "Human-readable description of the action",
  "actorId": "ID of the user who performed the action",
  "actorName": "Name of the user who performed the action",
  "actorEmail": "Email of the user who performed the action",
  "action": "Machine-readable action identifier",
  "actionDisplayName": "Human-readable action name",
  "target": "Type of resource that was affected",
  "targetId": "ID of the specific resource that was affected",
  "metadata": {
    // Additional context-specific information
  },
  "organizationId": "ID of the organization where the action occurred",
  "teamId": "ID of the team (if applicable)",
  "createdAt": "ISO timestamp when the action was recorded"
}
```

### Audit log targets (verbatim from "Audit Log format > Audit Log Targets")

```
USER            - User accounts and profiles
ROLE            - Custom roles and permissions
TEAM            - Team structures and memberships
SERVICE_ACCOUNT - API service accounts
ORGANIZATION    - Organization-level settings
```

*(Bullets reformatted to a fixed-width list for alignment; wording is verbatim.
Attribution: promptfoo docs "Enterprise > Audit Logging > Audit Log Targets".)*

### Worked example — `role_updated`, the only documented non-null `metadata`

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "description": "admin@example.com updated role Developer",
  "actorId": "user-456",
  "actorName": "Admin User",
  "actorEmail": "admin@example.com",
  "action": "role_updated",
  "actionDisplayName": "Role Updated",
  "target": "ROLE",
  "targetId": "role-202",
  "metadata": {
    "input": {
      "permissions": ["read", "write"],
      "description": "Updated developer permissions"
    }
  },
  "organizationId": "org-456",
  "teamId": null,
  "createdAt": "2023-11-08T10:30:15Z"
}
```

Note the shape for Claim 6: the payload is under `input`, i.e. the new state as
submitted. There is no prior-state field and no `previous`/`before` key anywhere
in the documented schema.

### Retrieval endpoint, parameters, and auth (verbatim from "Accessing Audit Logs")

```
GET /api/v1/audit-logs
```

- `limit` (optional): Number of logs to return (1-100, default: 20)
- `offset` (optional): Number of logs to skip for pagination (default: 0)
- `createdAtGte` (optional): Filter logs created after this ISO timestamp
- `createdAtLte` (optional): Filter logs created before this ISO timestamp
- `action` (optional): Filter by specific action type
- `target` (optional): Filter by specific target type
- `actorId` (optional): Filter by specific user who performed the action

Audit log access requires:

- Valid authentication token
- Organization administrator privileges

*(Attribution: promptfoo docs "Enterprise > Audit Logging > Accessing Audit
Logs". Note what is absent from the parameter list: any ordering, cursor, sort,
or export parameter.)*

### Example request and response envelope (verbatim)

```bash
curl -X GET \
  "https://your-promptfoo-domain.com/api/v1/audit-logs?limit=50&action=login" \
  -H "Authorization: Bearer YOUR_API_TOKEN"
```

```json
{
  "total": 150,
  "limit": 50,
  "offset": 0,
  "logs": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "description": "john.doe@example.com logged in",
      "actorId": "user-123",
      "actorName": "John Doe",
      "actorEmail": "john.doe@example.com",
      "action": "login",
      "actionDisplayName": "User Login",
      "target": "USER",
      "targetId": "user-123",
      "metadata": null,
      "organizationId": "org-456",
      "teamId": null,
      "createdAt": "2023-11-08T08:06:40Z"
    }
    // ... more log entries
  ]
}
```

`total` is the only published signal distinguishing "the window matched nothing"
from "the window was wrong" (Claim 13).

### Compliance bullets and troubleshooting list (verbatim)

- **SOC 2**: Provides detailed access logs and administrative change tracking
- **ISO 27001**: Supports access control monitoring and change management requirements
- **Data protection reviews**: Helps track data access and user management activities
- **HIPAA**: Provides audit trails for access to systems containing protected health information

1. Verify you have organization administrator privileges
2. Check that your API token is valid and has not expired
3. Ensure your query parameters are properly formatted

*(Attribution: promptfoo docs "Enterprise > Audit Logging > Compliance Usage" and
"> Troubleshooting".)*

### Related Enterprise pages read for context (not claims from this page)

Three cross-page facts that change how this page's claims land. Quoted verbatim
from their own pages:

- **Credential model** (`site/docs/enterprise/service-accounts.md`):
  "Only global system admins can create and assign service accounts." /
  "Service account API keys will not have programmatic access to Promptfoo
  Enterprise unless assigned to a team and role." / a global-admin key "will be
  provisioned with access to everything that can be done in the organization
  settings page".
- **RBAC vocabulary** (`site/docs/enterprise/teams.md`): "**Administrator**: Full
  access to everything in the team" (team-scoped) / "**Manage Configurations**:
  Create, edit, and delete configurations and plugin collections" /
  "**Manage Targets**: Create, edit, and delete targets".
- **No audit sink** (`site/docs/enterprise/webhooks.md`): webhooks "notify
  external systems when security vulnerabilities (issues) are created or
  updated", and the complete event list is `issue.created`, `issue.updated`,
  `issue.status_changed`, `issue.severity_changed`, `issue.comment_added` — five
  red-team finding events, no audit-log event. So the Enterprise webhook
  surface, which the page's sibling Enterprise overview advertises as
  "External Integrations (SIEMs, Issue trackers, etc.)", does not carry audit
  records.

Source for all artifacts: https://www.promptfoo.dev/docs/enterprise/audit-logging,
cross-checked against the page's own markdown source
(`site/docs/enterprise/audit-logging.md` in `promptfoo/promptfoo` @ `main`,
retrieved 2026-10-05). The two agree; the code blocks above are as authored
upstream, and prose quotes are the rendered page's visible text.

## Cross-References

- **Corroborates**:
  - `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` **Claim 17**
    ("Actor state is a real state machine with committed transitions, and each
    transition emits a record that is authoritative by resource rather than by
    message") — independently arrived at the same architectural object: a
    control-plane event stream whose records are authoritative about the
    resource, emitted after the state change, and paired with an explicit
    statement of what the stream will not tell you ("a gap looks the same as an
    actor that just sat still"). promptfoo's boundary sentence (Claim 2) is the
    same discipline in vendor form: declare the plane you cover before anyone
    relies on the trail. (Verified: Claim 17 heading, its two quotes, and the
    "gap looks the same" limit statement.)
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` **Lesson
    4** ("Credential rotation is the safety net when an observability leak is
    discovered — but it depends on knowing which credentials were exposed"; the
    lesson's action is to "cross-reference the exposure window with the
    provisioning timeline of each active credential") — this page documents
    `service_account_created` and `service_account_deleted` but **no rotation or
    re-issue event** (Claim 3), so the provisioning timeline that Lesson 4
    requires cannot be reconstructed from promptfoo's audit log: a rotated key
    has a creation record from its original issuance and no record of the
    rotation. Cited by section name because this is a failure-report note with
    `### Lesson N` headings, not numbered claims. (Verified: Lesson 4 heading,
    its two quotes, and the "provisioning timeline of each active credential"
    action text.)

- **Contradicts**:
  - **[#1597](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1597)**
    — *self-disagreement within this source*: the page frames Audit Logging as
    "forensic access information" and claims HIPAA / data-protection value from
    tracking access (Claim 1, Claim 10), while its own documented event taxonomy
    contains no access or read event — 14 administrative mutations plus a
    successful-login event — and its scope note assigns every data-plane
    operation to an unnamed "tracked separately" surface (Claim 2). The two
    readings give opposite answers to whether this artifact can answer an
    access-review question. Filed per MINER.md §4a from
    `.github/ISSUE_TEMPLATE/contradiction.yml`; per the same section **no
    verdict is picked in this note** — the resolver assigns the `C-NNN` entry.
    Until it is resolved the guide should carry the practical pair, which is safe
    under either verdict: enumerate the event taxonomy before citing a vendor
    audit log, and treat an events list with no read events as administrative
    change evidence only.
  - No contradiction with an existing note. The nearest adjacent material
    (`blog-promptfoo-mckinsey-lilli-appsec.md` Claim 7, whose audit checklist is
    about *application* attack surface, and `failure-litellm-host-header-auth-bypass.md`,
    whose "audit" usage is code-review hardening of route derivation) uses the
    word for different objects entirely; neither makes a claim about
    control-plane audit trails that this page opposes.

- **Extends**:
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` **Claim 3**
    ("Every outbound agent request becomes an audited span at the proxy" — "An
    OpenTelemetry Collector can persist those spans to an audit log, or we can
    feed them into observability and security tooling such as Jaeger, Grafana,
    or a SIEM platform") — the corpus now holds both audit-trail postures side
    by side, and they are opposites. There, the audit log is a *sink* a collector
    pushes spans into, per-request, continuously. Here, it is an *origin* you
    poll: one endpoint, a 100-record page ceiling, no documented ordering, and no
    push path at all (Claim 7, Claim 8, and the webhook evidence in Concrete
    Artifacts). The guide's push-vs-pull framing for audit trails now has a
    worked instance on each side; promptfoo's side is the one to cite when the
    requirement is "the SIEM must hold the trail", because polling a 100-record
    page is not a SIEM feed. That note's **Claim 5** ("Like any control plane,
    it must be hardened against compromise and failure") also applies verbatim to
    this artifact: the audit log is the record of control-plane compromise, so an
    attacker who reaches the control plane is editing both the system and its
    forensic record. (Verified: Claim 3 and Claim 5 headings and quotes.)
  - `source-notes/failure-litellm-guardrail-logging-secret-exposure.md` **Lesson
    1** ("Observability/logging integrations are data-exposure surfaces and must
    apply the same sanitization as any other output path") and **Lesson 3**
    ("Least-privilege access to observability backends is a security control, not
    just a cost/compliance measure") — both compose directly with Claims 5 and 8.
    Every audit record carries `actorEmail` (PII per row), and the documented way
    to move those records anywhere is to copy them out under an
    organization-administrator credential that, per the service-accounts page, is
    also able to manage users, roles, teams, and webhooks. So pulling this feed
    into a collector is an egress decision (identity data, one email per row)
    taken with an admin credential (no documented read-only scope) — the same
    shape Ch06 already flags for guardrail payloads. The guide's egress-decision
    rule should say "an audit trail is an output path too". (Verified: Lesson 1
    and Lesson 3 headings and quotes.)
  - `source-notes/blog-linsun-pod-deployment-unit-ai-agent.md` **Claim 12**
    (three concrete ways actor attribution is *not* solved, including "actor
    identity cannot be sampled out of the lifecycle stream without creating
    silent wrongness") — read alongside Claim 5, this note adds a fourth
    documented attribution failure mode the corpus had not recorded: the audit
    record carries no source-IP or session field, so a stolen admin token
    produces a record indistinguishable from the legitimate session. The
    composite rule for the guide: an audit record that cannot distinguish
    legitimate from illegitimate use of a credential is a *notification* of
    change, not evidence of who was present.

- **Novel**: This is the corpus's **first** source on a control-plane audit trail
  for an eval/red-team platform, and every one of the following is net-new:
  1. **The event taxonomy as a citable, closed list** (Claim 3) — 15 action
     identifiers over 5 target types, the corpus's only enumerated
     "what-audit-log-actually-records" contract.
  2. **The control-plane / data-plane boundary as an explicit vendor statement**
     (Claim 2) — audit coverage of the plane that administers the product is not
     audit coverage of the product's work.
  3. **The taxonomy/scope self-disagreement** (Claims 1, 10) — a feature framed
     as *access* forensics whose event list contains no access events, filed as
     #1597. This is the corpus's sharpest instance of the "compliance bullet is
     not a control specification" pattern.
  4. **The documented absences as a first-class finding** (Claims 3, 6, 7, 9,
     11): no failed-login event, no read/access events, no key-rotation event, no
     config/plugin/target event, no before/after diff, no retention window, no
     export or webhook path, no ordering guarantee, and a documented
     `ORGANIZATION` filter with no documented producer.
  5. **Pull-only collection arithmetic** (Claim 7) — offset pagination over an
     always-appending, unordered stream with a 100-record ceiling, and the
     `total`-not-`logs.length` rule for distinguishing "no activity" from "bad
     query" (Claim 13).
  6. **Audit-read as an admin capability** (Claim 8) — the retrieval credential's
     documented scope is organization administration, with no read-only tier, and
     three unreconciled privilege vocabularies across the Enterprise pages.
  The guide has **no** prior coverage of eval-platform audit trails: `grep -i
  audit guide/*.md` returns only Ch06's GB 45438 retention rule, its agent
  decision-trail Rule, and unrelated uses of the verb. Ch06 §Agent auditability
  (`guide/06-security-and-trust.md:598`) currently asserts that audit records
  should be "structured, queryable" without saying *which plane* has to be
  inside them — this source is the evidence that makes that distinction
  load-bearing.

## Guide Impact

- **Chapter 06 §"Agent auditability is becoming a compliance expectation"
  (`guide/06-security-and-trust.md:587`) — add the plane distinction to the
  existing Rule, which currently requires "structured, queryable audit records"
  of the agent decision trail with no statement of which plane must produce
  them. Add: **an audit trail that covers only the control plane does not
  satisfy an auditability requirement for the workload.** Support it with the
  vendor's own boundary sentence (Claim 2) and with the concrete consequence for
  an eval platform: promptfoo's documented trail can attribute who was made an
  admin but not who edited the assertion that passed a gate, because
  configuration, plugin, and target changes have no action in the taxonomy while
  the RBAC layer treats them as governed resources (Claims 3, 11). Proposed rule
  text: *for every resource a decision depends on, name the audit event; a
  resource with no event is ungoverned, and no amount of IAM logging substitutes.*
- **Chapter 06 §"China's GB 45438-2025: labeling, provenance, and log
  retention" (`guide/06-security-and-trust.md:525`) — the existing Rule requires
  planning retention windows against the applicable regulation. Add the
  converse, which this source makes concrete: **a log with no documented
  retention window and no export path cannot be cited as evidence for a
  retention requirement.** promptfoo's audit-logging page states no retention
  period, documents no bulk export, and routes all retrieval through a
  100-record-capped poll (Claims 7, 9), while still asserting HIPAA value
  (Claim 10). A procurement-time check — "state the retention window, name the
  export path, list the events" — turns a vendor compliance bullet into a
  three-question gate that this page fails on all three.
- **Chapter 06 §"A guardrail is an egress boundary — configure what crosses it"
  (`guide/06-security-and-trust.md:547`) — extend the egress-decision rule to
  audit trails. This page's records carry `actorEmail` on every row (Claim 5) and
  leave the platform only via an admin-scoped credential with no documented
  read-only scope (Claim 8), which is the exact shape of the
  `failure-litellm-guardrail-logging-secret-exposure.md` incident — an identity-
  bearing internal record forwarded to an external store. Rule to add: *treating
  an audit trail as structured, queryable evidence means it will be copied into
  a collector; that copy is an egress decision and needs the same minimization
  review as a guardrail payload.*
- **Chapter 06 §Trust rollout patterns — one line on control-plane hardening.**
  Add that an audit log is the record of control-plane compromise, so it inherits
  the corpus's standing control-plane caution
  (`blog-cncf-network-boundary-ai-agents-nginx-otel.md` Claim 5): the component
  whose compromise rewrites the forensic record must be hardened and monitored
  as infrastructure, not treated as a reporting surface.
- **Chapter 05 §"Evaluation and measurement methodology" — gate provenance.**
  Add the audit-taxonome-to-gate-dependency test described above, using promptfoo
  as the worked example (Claims 3, 11): enumerate the objects a passing eval
  depends on — assertions, judge model, rubric, provider config, target — and
  require each to be auditable. Under promptfoo's documented taxonomy none of
  them is. This is a companion to Ch05's existing "A gate that cannot fail is not
  a gate" (`guide/05-llm-ops-reliability.md:655`): that Rule covers a gate that
  reports green without verifying; this covers a gate that verifies and cannot be
  shown to have verified the same thing twice.
- **Chapter 02 (Observability) — two collector rules for audit trails.** Add
  the derived operational rules as concrete guidance, since they generalize past
  this vendor: (1) *never page an append-only event stream with `offset` and no
  ordering guarantee — pin a closed `createdAt` window, dedupe on record `id`,
  advance from the maximum timestamp observed* (Claim 7); (2) *assert on the
  response's `total`, not on the returned page length, before concluding "no
  activity occurred"* — an empty page is indistinguishable from a broken query,
  and the only documented signals of a broken query are the precondition checks
  (Claims 7, 13). Present both as vendor-independent collector discipline, with
  promptfoo's parameter names as the concrete instance.
- **Do not** cite this page as evidence that an eval platform is
  compliance-ready. It is evidence of what a documented control-plane audit trail
  contains and, equally, of how far a vendor compliance section can run ahead of
  its own schema. Until #1597 is resolved, carry the access-coverage question as
  a `**Debated:**` pair rather than adopting either reading.

## Extraction Notes

- Source read in full via direct fetch of the rendered page
  (https://www.promptfoo.dev/docs/enterprise/audit-logging), then diffed against
  the page's own markdown source (`site/docs/enterprise/audit-logging.md` in
  `promptfoo/promptfoo` @ `main`, retrieved 2026-10-05) so that every quote and
  every code block is character-for-character as authored upstream rather than
  as re-rendered by HTML extraction. The two agree — including the two passages
  that HTML extraction mangles (`"[email protected]"` in the examples versus
  `john.doe@example.com` in the source, and collapsed whitespace inside the JSON
  blocks). Prose quotes above are the **rendered** page's visible text; where the
  source markdown carries link syntax (e.g. "Promptfoo Enterprise"), the visible
  text is quoted, which is what a reader sees at the URL.
- **Sub-pages followed** (4 of the 5-permitted budget), all read in full and
  used only for context, never as claim sources — each is attributed in Concrete
  Artifacts: `docs/enterprise/service-accounts.md` (the retrieval credential),
  `docs/enterprise/teams.md` (RBAC vocabulary and the governed config/target
  resources), `docs/enterprise/webhooks.md` (the absence of an audit sink),
  `docs/enterprise/authentication.md` (the authentication surface that the
  single `login` event does not describe). `docs/enterprise/index.md` was read
  for the Enterprise comparison matrix ("External Integrations (SIEMs, Issue
  trackers, etc.)"), which is where the webhook/audit asymmetry shows up.
- **Not retrievable**: the page's designated "complete API documentation" target,
  `/docs/api-reference/#tag/audit-logs`, returns no content body when fetched
  (client-rendered spec), and `promptfoo/promptfoo` contains no
  `site/docs/api-reference` file at the referenced path, nor any
  `openapi.json` / `openapi.yaml` / `api-schema.json` under `site/static/`.
  Claim 9 records this as the boundary of the documented contract.
- **Implementation cross-check (not a claim source).** Because this page
  describes an Enterprise-gated control plane, I checked whether the feature is
  implemented in the open-source repository. It is not: a code search across
  `promptfoo/promptfoo` for `audit-logs` returns exactly **one** hit — this
  page's own markdown — and a search for `audit` returns 236 hits that are all
  the unrelated **Model Audit** product (`src/models/modelAudit.ts`,
  `src/types/modelAudit.ts`, `site/docs/model-audit/*`). So no claim above is
  code-verifiable, none of the runtime behavior (ordering, delivery, retention,
  `metadata` richness beyond the three illustrations) can be checked against an
  implementation, and this is why `confidence_overall` is `emerging` rather than
  `settled`: the taxonomy and schema are a *specification* we trust because it
  is the vendor's own contract, and Claims 9 and 12 mark the line between that
  and unverified runtime behavior.
- **Candidate handling** (`miner-related-notes.md`, 10 lexical candidates — all
  from the generic token overlap of "audit"/"limits"/"teams", none about audit
  logging). Cited: none by the retrieval list itself; two cross-refs above were
  found by searching `source-notes/` directly (`blog-linsun-pod-deployment-unit-ai-agent.md`,
  `blog-cncf-network-boundary-ai-agents-nginx-otel.md`) plus the two LiteLLM
  notes the Prospector named. Explicitly dismissed, one line each:
  `docs-litellm-batches-api.md` — batch-admission quota semantics, no audit or
  control-plane content; `docs-google-sre-reliable-product-launches.md` — launch
  checklists and coordination, no audit-log contract; `blog-pagerduty-sre-agent-triage.md`
  — incident triage and alert routing; `docs-promptfoo-pi-scorer.md` — grader
  configuration, though its Claim 3 is the corpus's precedent for how to treat a
  promptfoo vendor assertion published without evidence, which is the
  calibration bar used for Claim 10;
  `docs-langfuse-mcp-server.md` — docs-MCP transport; `docs-google-sre-eliminating-toil.md`
  — the toil taxonomy, adjacent only in that a manual compliance pull would be
  toil, which no source documents anyone doing;
  `docs-google-sre-team-lifecycles.md` — SRE org design, no RBAC event model;
  `docs-promptfoo-deterministic-metrics.md` — assertion types;
  `blog-promptfoo-owasp-red-teaming.md` — red-team method, though it is the
  natural counterpoint: red-team *findings* have a documented delivery path
  (five `issue.*` webhook events), while audit records do not;
  `blog-promptfoo-red-team-claude.md` — `reasoning-dos` plugin configuration.
  Also considered and dismissed as a cross-ref:
  `docs-litellm-gateway-auth-reference.md` (named by the Prospector) — its Claim
  7 permission-resolution asymmetry (six levels for MCP, two for A2A) has no
  promptfoo counterpart, because promptfoo's problem is the opposite: three
  privilege vocabularies for one role and no resolution table (Claim 8).
- **Contradiction filing decision.** One contradiction issue was filed,
  [#1597](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1597),
  scoped narrowly to the single material self-disagreement (the "access"
  framing and compliance claims vs. an event taxonomy with no access events).
  Checked first against `CONTRADICTIONS.md` (no entries beyond the bootstrap
  note) and the 16 open `contradiction`-labeled issues (none covers promptfoo
  audit logging). Deliberately **not** filed, as cross-page documentation gaps
  rather than contradictions, following the precedent set in
  `docs-promptfoo-configuration-rate-limits.md` Claim 13: (a) the Enterprise
  overview matrix advertising "External Integrations (SIEMs, Issue trackers,
  etc.)" against the webhook page's five `issue.*` events — a marketing-matrix
  vs docs gap about *red-team findings*, not a claim this page makes;
  (b) the three privilege vocabularies across the audit-logging,
  service-accounts, and teams pages — an ambiguity, not an opposition, and it
  cannot yet be shown which page is wrong; (c) "comprehensive audit logs" in
  this page's frontmatter against its own scope note — folded into #1597, since
  it is the same access-coverage disagreement in vendor-marketing dress.
- `registry/sources.json` and `registry/claims-index.json` were **not** touched;
  both are derived indexes rebuilt by `registry-rebuild.yml` after merge.