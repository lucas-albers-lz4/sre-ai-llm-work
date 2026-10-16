---
source_url: https://www.promptfoo.dev/docs/enterprise/teams
source_type: docs
title: "Promptfoo Enterprise: Managing Roles and Teams — Persisted CLI Team Context, the Team-Scoped/Org-Scoped Isolation Rule, and the Seven-Permission RBAC Inventory"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-15
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: emerging
issue: "#1626"
---

# Promptfoo Enterprise: Managing Roles and Teams

> Team context in the promptfoo Enterprise CLI is persisted local state, not a
> per-command flag: `promptfoo auth teams set` routes all subsequent operations
> (evals, sharing, scans) to the selected team, the vendor's own remedy is a
> `promptfoo auth whoami` pre-flight before sharing or scanning, and the page's
> isolation rule splits tenancy in two — resources are team-scoped, API keys are
> org-scoped — alongside a verbatim seven-permission inventory whose `Run
> Scans` permission already bundles "view results".

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Managing Roles and Teams" page). Page header carries the gating
  notice "This feature requires Promptfoo Enterprise." Page footer: "Last
  updated on **Oct 15, 2026** by **renovate\[bot\]**" (a dependency bump, not
  an editorial change — `date_published` above is that last-updated stamp; the
  page publishes no original publication date).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor,
  documenting its own Enterprise control plane. Authoritative *as a
  specification* of the team-context commands, the isolation rule, and the RBAC
  vocabulary — all string-checkable against the page itself, and against a live
  Enterprise tenant. It is not measurement: no configuration surface, no API
  endpoints, no enforcement semantics, and nothing here is verifiable in the
  open-source repository (Enterprise-gated hosted feature).
- **Scope**: Covers creating teams, adding members with roles, creating custom
  roles, the CLI team-context commands (`teams set`, `whoami`, org switch via
  API key), the three-bullet team-isolation rule, team-level service accounts,
  and the seven-permission list. Does **not** cover: default/predefined role
  definitions or any permission→role mapping, role inheritance, resource-level
  (per-item) ACLs, a permission introspection command, rate limits/quotas,
  error codes, CI-gating semantics (thresholds, webhooks, status checks,
  pass/fail), or what any of this looks like in the audit log (that half is
  `docs-promptfoo-enterprise-audit-logging.md`, issue #1589).
- **Sibling/linked pages followed** (2 of the 5-permitted budget), used for
  context and explicitly attributed where quoted: `/docs/enterprise/service-accounts/`
  (fetched directly — the sibling authority statement for the admin gate and the
  mandatory team+role binding of machine keys) and `/docs/enterprise/authentication/`
  (read via its dedicated corpus note `docs-promptfoo-enterprise-authentication.md`,
  issue #1590, which deep-reads it — its Claims 7, 9, and 10 cover the same CLI
  team surface from the identity side).

## Extracted Claims

### Claim 1: CLI team context is persisted ambient state, not a per-command flag — `promptfoo auth teams set "Your Team Name"` routes all subsequent CLI operations to that team
- **Evidence**: The "CLI Team Context > Setting Your Active Team" section: the
  command block plus the unqualified scope sentence immediately under it. The
  authentication note (its Claim 7) adds the persistence half from the sibling
  page: "Your selection persists across CLI sessions."
- **Confidence**: settled (documented CLI contract; the persistence detail is
  corroborated by the sibling page per the authentication note's Claim 7)
- **Quote**: "All subsequent CLI operations (evaluations, sharing results, etc.) will use this team context."
- **Our assessment**: Buy it, and this is the claim the Prospector's key
  question was about: which team a result lands in is decided by *local state
  left behind by an earlier command*, not by an explicit flag on the run that
  matters. Combined with the sibling page's cross-session persistence, a stale
  team context survives CLI restarts — so on a shared or long-lived CI runner
  the next `promptfoo eval --share` or red-team scan silently writes into
  whatever team the last operator (or previous job) selected, with no prompt and
  no error. This is the mis-attribution footgun the note exists to record: the
  failure mode is *results in the wrong team*, and it is silent by design of
  the state model. Operational rule for the guide: treat team context like any
  other ambient job state (cf. env-var scoping discipline) — either pin it
  explicitly at job start (`auth teams set` in the bootstrap step) or assert it
  (Claim 2) before the run that publishes or scans.

### Claim 2: The vendor's own remedy for that footgun is a pre-flight `promptfoo auth whoami`, tied explicitly to the mis-destination failure mode — and it is the only documented verification
- **Evidence**: The "Verifying Team Context" subsection and the closing tip
  block of "Team Isolation". No other verification command, flag, or output
  format appears anywhere on the page.
- **Confidence**: settled (documented procedure and advisory)
- **Quote**: "Always verify your team context with `promptfoo auth whoami` before sharing evaluation results or running scans to ensure they go to the correct team."
- **Our assessment**: Buy it — the tip is the vendor conceding the failure
  mode in Claim 1: the sentence presupposes that results *can* go to the wrong
  team and that the damage happens at share/scan time. Note what the remedy is
  and what it is not: `whoami` "displays your current organization and team" —
  a human-readable display, with no documented machine-readable output, no
  expected-value assertion, and crucially **no gate**: nothing stops a scan
  from running with a wrong or unset context; the check is advisory and
  upstream. So the documented safety property is *detectable*, not *prevented*,
  and a CI pipeline that wants the property must wrap `whoami` itself (grep the
  expected team, fail otherwise) — the platform provides the readout, not the
  guard. This is the bounded, novel extraction target for the guide: a concrete
  pre-flight check pattern (`teams set` → `whoami` assert → run) that the
  corpus can recommend as *operator discipline* while stating plainly that the
  product does not enforce it.

### Claim 3: The isolation rule is two-level tenancy — resources are team-scoped, API keys are org-scoped, and team selections are remembered independently per organization
- **Evidence**: The three "Team Isolation" bullets, verbatim below in Concrete
  Artifacts. The org-switch mechanism is stated in the same bullet list.
- **Confidence**: settled (the three bullets are the vendor's stated isolation
  contract)
- **Quote**: "**Resources are team-scoped**: Evaluations, configurations, and results are associated with your active team" / "API keys are scoped to one organization. To switch organizations, run `promptfoo auth login --api-key <apiKey>` with a key from that organization"
- **Our assessment**: Buy it as the layering model: **the credential picks the
  organization (org-scoped key), and ambient CLI state picks the team within
  it (per-org remembered selection)** — two different mechanisms, and only the
  first one is a credential. For CI/CD service accounts (Claim 4) that split is
  the operational hazard: a pipeline key is org-bound, but where its results
  land is still decided by mutable local state, so tenant isolation (via key
  custody) holds while *intra-org team attribution* depends on the job
  remembering to set context. The per-org independence is the reassuring half —
  team selections do not leak across organizations, so switching orgs cannot
  inherit another tenant's team pin — but it also means there is no single
  global context to rely on across tenants. Per the Prospector's attribution
  guidance, the org-switch command itself is owned by
  `docs-promptfoo-enterprise-authentication.md` **Claim 9** (verified: heading
  reads "Switching organizations is done by presenting a different org's API
  key — `promptfoo auth login --api-key <apiKey>` — so the key's org defines
  the tenant boundary"); this note records only that the Teams page restates it
  as part of the isolation triad.

### Claim 4: Team-level service accounts are the documented CI/CD identity path, but creation is admin-gated — "Only system admins can create service accounts"
- **Evidence**: The note block under "Creating Teams". The sibling
  service-accounts page (fetched) words the same gate one notch stricter and
  adds the binding requirement.
- **Confidence**: settled (both pages state the gate directly; the wording
  variance below is observed, not inferred)
- **Quote**: "Only system admins can create service accounts."
- **Our assessment**: Buy it as a provisioning-order dependency for pipeline
  bootstrap: no self-service machine identity — a human with system-admin
  authority must exist and act before any CI key can be minted, so
  "automate the pipeline first" is not possible on this platform without a
  pre-provisioned admin. Per the Prospector's instruction this claim is
  *folded, not duplicated*: `docs-promptfoo-enterprise-service-accounts.md`
  **Claim 1** (verified: "Creation is a privileged operation — only global
  system admins can create and assign service accounts") owns the canonical
  form, including the display-once key and inert-until-bound semantics, which
  stay out of this note. Two observations worth carrying anyway. (a) **Wording
  variance**: this page says "Only system admins"; the sibling says "Only
  global system admins" — same authority class, but it is a fourth spelling in
  a cluster the audit-logging note already flagged as unreconciled (its Claim 8:
  "Three vocabularies, no mapping" across "Organization administrator", "global
  system admin", and team "Administrator"). (b) The teams page's framing —
  "You can also create service accounts at the team level" — presents the
  machine identity as a team-level object while the sibling page's actual
  creation path is Organization Settings → Users, i.e. the *creation* is
  org-level-admin and the *binding* is team-level. Contextual difference in
  emphasis, not opposing claims — no contradiction issue filed (MINER §4a:
  conditioning/framing variance, both sides describe the same flow).

### Claim 5: The RBAC inventory is exactly seven named permissions, verbatim — and `Run Scans` already bundles "view results", so execution separates from *mutation* of results, not from reading them
- **Evidence**: The "Permissions" section, presented as the supported set
  ("Promptfoo Enterprise supports the following permissions:"); all seven
  strings reproduced verbatim in Concrete Artifacts.
- **Confidence**: settled (enumerated vendor contract — the strings are the
  citable vocabulary, directly checkable against a tenant's role editor)
- **Quote**: "**Run Scans**: Run scans and view results" / "**View Results**: View issues and evaluations" / "**Manage Results**: Edit and delete evaluations and issues"
- **Our assessment**: Buy the inventory, and correct one piece of shorthand
  from the triage discussion: the seven strings show that **`Run Scans` is not
  separable from viewing results** — its own definition is "Run scans and view
  results". What *is* separable is execution and *mutation*: `Manage Results`
  ("Edit and delete evaluations and issues") is a distinct grant, so a CI
  identity can hold `Run Scans` without the ability to edit or delete what it
  (or anyone else) produced — the raw material for a least-privilege scan
  runner whose output is read-only to itself. The read surface then splits
  three ways: `Run Scans` implies view of scan results, `View Results` covers
  "issues and evaluations" (the review surface, including findings triage), and
  `Manage Results` is the only writer. Limits on how far to take this: the page
  maps **no permission to any role** (no default roles are enumerated here or
  on the sibling page, which only says "Select the predefined role" — Claim 7),
  documents no resource-level scoping beyond the team, and never mentions CI
  gating, so this vocabulary can be cited as the *permission model* but not as
  evidence that any particular pipeline setup is achievable or enforced.

### Claim 6: Role assignment is per team membership, not per user — the role is set "of the user in the team", so access review means enumerating memberships
- **Evidence**: The "Creating Teams" member-add sentence and the "Creating
  Roles" section (custom roles creatable from the "Roles" tab, no role
  templates published). The sibling service-accounts page applies the same axis
  to machine identities: assignment is to "a team" with "the predefined role
  for the service account for that team".
- **Confidence**: settled (the assignment axis is stated; the multi-role
  corollary is a direct reading of a role being a property of membership)
- **Quote**: "You can add users to a team by editing the team and clicking the \"Add team members\" button. This will also allow you to set the role of the user in the team."
- **Our assessment**: Buy it. The RBAC assignment object is the *membership
  row* (user × team → role), not the user, so the same human can hold
  different permissions in different teams, and "what can this person do" is
  unanswerable without the team list. That has two guide-relevant
  consequences: (1) offboarding review must walk team memberships, not just
  the user directory — remove-the-user and remove-the-membership are
  different operations, and only one is implied by "user_removed" in the audit
  taxonomy (which does have `user_removed_from_team` and
  `user_role_changed_in_team` — see the audit note's Claim 3 team-management
  category); (2) human and machine identities share the assignment axis
  (service accounts are bound to team + role the same way), so one mental model
  covers both. Notably absent: any statement that roles are assignable at the
  *organization* level — every role grant on this page is scoped to a team
  ("Full access to everything in the team"), which is exactly the tension the
  audit-logging note recorded when an org-wide audit read requires
  "Organization administrator" privileges (its Claim 8).

### Claim 7: The page documents no role definitions, no permission→role mapping, no permission-check command, and no CI-gating semantics — it is a UI walkthrough plus a permission table
- **Evidence**: Negative finding from a full read: no default/predefined role
  is named (the sibling page says only "Select the predefined role"); no
  command, flag, or endpoint returns the caller's effective permissions
  (only `whoami`, which shows org + team, not role); no threshold, webhook,
  status-check, pass/fail, or pipeline vocabulary appears anywhere; no
  configuration keys or environment variables are shown.
- **Confidence**: settled as a statement of what this page says (absence
  verified by full read; per corpus convention, undocumented ≠ nonexistent)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This is the calibration claim that bounds Claims 1–6, and
  it matches the Prospector's scope limit: the CI-gating angle is *inferable*
  — service accounts exist "for CI/CD pipelines and automated testing" (Claim
  4's context sentence) and `Run Scans` is a grantable execution permission —
  but the page never describes how a scan result becomes a gate. Do not let
  this note's existence let the guide claim promptfoo Enterprise provides
  CI gating, role templates, or permission introspection. The absence is
  corroborated across the enterprise cluster rather than unique to this page:
  the findings page likewise "contains no CI gating"
  (`docs-promptfoo-enterprise-findings-reports.md` **Claim 11**, verified) and
  the webhook surface documents no scan/eval completion event to gate on
  (`docs-promptfoo-enterprise-webhooks.md` **Claim 1**, verified: "there is no
  `scan.started`, `eval.completed`, `guardrail.tripped`, or audit event").
  Whether the *product* lacks these features is unknown; whether the
  *documentation* does is settled.

### Claim 8: The isolation bullet's resource enumeration ("Evaluations, configurations, and results") is narrower than the permission table it sits beside — targets, plugin collections, issues, and webhooks are governed or accepted by the team surface but never named as team-scoped
- **Evidence**: Cross-reading the page's own two lists: the "Resources are
  team-scoped" bullet names three classes; the permission table governs
  additional object types (`View Configurations` covers "configurations,
  targets, and plugin collections"; `View Results`/`Manage Results` cover
  "issues and evaluations"); and the sibling webhook config accepts an optional
  `teamId` field whose semantics its own page leaves open.
- **Confidence**: emerging (the two lists are verbatim and their
  non-co-extension is directly observable; what is *not* documented is whether
  "configurations" in the isolation bullet is intended broadly enough to cover
  targets/plugin collections — we record the gap, not a product defect)
- **Quote**: "**View Configurations**: View configurations, targets, and plugin collections"
- **Our assessment**: Read as an incomplete enumeration, not a self-
  disagreement — nothing on the page denies that targets are team-scoped; the
  page simply never says so, while granting a team permission over them. That
  keeps it inside MINER §4a's "when NOT to file" (no opposing claims), but the
  gap is operationally live: an operator asking "which team owns this target?"
  or "does this red-team finding belong to team X?" has no documented answer
  from this page. It also extends an open question in
  `docs-promptfoo-enterprise-webhooks.md` **Claim 5** (verified: its assessment
  notes "the webhook is org-wide with an optional `teamId`; the page does not
  document what `teamId` actually scopes") — the Teams page defines
  team-scoping for three resource classes, and webhooks are not among them, so
  that note's question remains open rather than resolved. Guide-safe phrasing:
  *team-scoped resources, as documented, are evaluations, configurations, and
  results; everything else's team association is undocumented.*

## Concrete Artifacts

*(Source: https://www.promptfoo.dev/docs/enterprise/teams — rendered page,
retrieved 2026-10-16.)*

### CLI team-context commands (verbatim, "CLI Team Context")

```
promptfoo auth teams set "Your Team Name"
```

After logging in, set your active team using the command above; "All
subsequent CLI operations (evaluations, sharing results, etc.) will use this
team context."

```
promptfoo auth whoami
```

"Before running important operations, verify your active team" — "This
displays your current organization and team."

Org switch (verbatim, "Team Isolation > Organization selection"):

```
promptfoo auth login --api-key <apiKey>
```

### Team Isolation bullets (verbatim)

- **Organization selection**: API keys are scoped to one organization. To switch organizations, run `promptfoo auth login --api-key <apiKey>` with a key from that organization
- **Team selections are isolated per organization**: If you have access to multiple organizations, each organization remembers its own team selection independently
- **Resources are team-scoped**: Evaluations, configurations, and results are associated with your active team

### Admonition blocks (verbatim)

> Only system admins can create service accounts.
> *(note block, "Creating Teams")*

> Always verify your team context with `promptfoo auth whoami` before sharing evaluation results or running scans to ensure they go to the correct team.
> *(tip block, "Team Isolation")*

### Complete permission inventory (verbatim, "Permissions")

Promptfoo Enterprise supports the following permissions:

- **Administrator**: Full access to everything in the team
- **View Configurations**: View configurations, targets, and plugin collections
- **Run Scans**: Run scans and view results
- **Manage Configurations**: Create, edit, and delete configurations and plugin collections
- **Manage Targets**: Create, edit, and delete targets
- **View Results**: View issues and evaluations
- **Manage Results**: Edit and delete evaluations and issues

*(Attribution: promptfoo docs "Enterprise > Managing Roles and Teams >
Permissions".)*

### Cross-page context (attributed, not claims of this page)

From `/docs/enterprise/service-accounts/` (fetched 2026-10-16):

- "Only global system admins can create and assign service accounts."
- "Service account API keys will not have programmatic access to Promptfoo Enterprise unless assigned to a team and role."
- "Select the predefined role for the service account for that team."

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing this
section; every listed path is cited or dismissed by name):

- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **cited**
  (Corroborates — Claim 7 above; its Claim 11).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  rate-limit accounting for `POST /v1/batches`; unrelated product, no
  team/RBAC/CLI-context content.
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**: AI-incident
  triage via an SRE Agent. Its Claim 5's "team-bounded boundaries" is agent
  skill scoping in a different product — thematic echo of the idea that
  authorization should bound a runner's reach, but no overlapping claim about
  tenant teams or RBAC vocabularies; not cited as agreement.
- `source-notes/docs-promptfoo-enterprise-authentication.md` — **cited**
  (Extends / Corroborates — Claims 1, 3 above; its Claims 7, 9, 10).
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization and measurement; unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE team
  organization/lifecycles — "team" here means an SRE org unit, not a promptfoo
  tenant team; no overlap (same dismissal the sibling notes made).
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **cited**
  (Corroborates / Extends — Claims 4, 6 above; its Claim 8, Claim 11, and its
  "Related Enterprise pages read for context" section).
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — **cited, narrowly**
  (Extends — Claim 7's permission-mapping absence; see below), otherwise
  dismissed as an overlap: its enforcement contract (Claim 1, Bearer
  `PROMPTFOO_API_KEY`) is guardrail-API authorization, not team RBAC.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: third-party
  scoring-model grader using `WITHPI_API_KEY`; unrelated credential.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: Langfuse docs MCP
  server, unauthenticated public endpoint; unrelated vendor surface.

Additional cross-references found by searching `source-notes/` and from the
Prospector's overlap list: `docs-promptfoo-enterprise-service-accounts.md`,
`docs-promptfoo-enterprise-webhooks.md` — handled below.

**Primary cross-references (verified per MINER §4b — every cited claim
heading re-read in the source note before writing):**

- **Corroborates**:
  - `source-notes/docs-promptfoo-enterprise-authentication.md` **Claim 7**
    ("The team CLI surface is three commands — `promptfoo auth teams list |
    set | current` — and the team selection persists across CLI sessions") —
    the identity-side record of the same state model this page documents from
    the operations side: this page says what the context *does* ("All
    subsequent CLI operations … will use this team context", Claim 1), that
    page says it *persists* ("Your selection persists across CLI sessions").
    Together they establish that team context is durable local state — the
    premise of the footgun analysis in Claims 1–2. (Verified: claim heading
    and quotes re-read.)
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` — its
    **"Related Enterprise pages read for context"** section already quotes
    three of this page's seven permission strings verbatim
    ("**Administrator**: Full access to everything in the team" /
    "**Manage Configurations**: …" / "**Manage Targets**: …") as RBAC
    vocabulary; this note supplies the full seven (Claim 5) as a first-class
    artifact rather than cross-page context. Its **Claim 11** also treats
    "Manage Configurations" and "Manage Targets" from this page as the governed
    resources whose absence from the audit taxonomy is the finding — i.e. the
    audit note's most consequential absence claim *depends on* this page's
    permission table, which until now it only partially quoted. (Verified:
    section and claim headings re-read.)
  - `source-notes/docs-promptfoo-enterprise-service-accounts.md` **Claim 1**
    ("Creation is a privileged operation — only global system admins can
    create and assign service accounts") — owns the canonical admin-gate claim
    this page restates in abbreviated form ("Only system admins can create
    service accounts", Claim 4); corroborates in direction, with the observed
    wording variance recorded there. (Verified: claim heading and quote
    re-read, and both live pages fetched to compare the two sentences
    character-for-character.)
- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-authentication.md` **Claim 10**
    ("Team context is a scoping input to execution, not display state — all
    subsequent operations, including red-team scans, run under the selected
    team until it is switched") — that note ends by pointing at this page for
    the advisory half ("The Teams doc adds the explicit advisory: verify with
    `promptfoo auth whoami` 'before sharing evaluation results or running
    scans.'"). This note is the extraction of that deferred surface: the
    advisory verbatim (Claim 2), the isolation triad (Claim 3), and the
    permission inventory that determines *who may* switch context and scan at
    all (Claims 5–6). Read together: authentication says the context scopes
    execution; teams says how you set, verify, and are permissioned for it.
    (Verified: claim heading and quote re-read.)
  - `source-notes/docs-promptfoo-enterprise-webhooks.md` **Claim 5** — its
    assessment records that a webhook config accepts an optional `teamId` whose
    scoping the webhook page never defines; this page's three-class resource
    enumeration (Claim 8) neither includes webhooks nor resolves that question,
    so the gap is now bounded by two pages of evidence instead of one. (Verified:
    claim heading and the `teamId` passage re-read.)
  - `source-notes/docs-promptfoo-enterprise-guardrails.md` — its
    **Concrete Artifacts → Troubleshooting: "Policies not updating after new
    red team tests"** section carries "Check permissions. Regeneration requires
    guardrail creation permissions." — and *guardrail creation* is not among
    the seven permission strings this page presents as the supported set
    (Claim 5). Cited by section name per MINER §4b. Either the troubleshooting
    line maps regeneration onto a differently-named grant (e.g. `Manage
    Configurations`) or the permission list is not exhaustive of role
    capabilities; the mapping is undocumented either way, which is precisely
    the Claim 7 absence (no permission→role mapping) — consistent with the
    audit note's "three vocabularies, no mapping" finding, and recorded as an
    open mapping question rather than a contradiction (no opposing claim
    exists on either page).
- **Contradicts**: **None identified, and no contradiction issue filed.**
  Checked against `CONTRADICTIONS.md` (format-only file; no `C-NNN` entries)
  and the open `contradiction`-labeled issues (#1150, #1307, #1322, #1338,
  #1352, #1408, #1461, #1462, #1486, #1514, #1517, #1534, #1548, #1550, #1562,
  #1565, #1591, #1593, #1597, #1633) — none touch promptfoo teams, RBAC, or
  team/CLI context. Two candidate tensions were checked rather than assumed:
  (a) the "system admins" vs "global system admins" wording between this page
  and the service-accounts page (Claim 4) — framing variance on the same flow,
  not opposing claims; (b) the resource-enumeration narrowness (Claim 8) and
  the guardrail-permission mapping (Extends) — both are documented *gaps*, and
  a gap is not a disagreement with any existing note's claim. Per MINER §4a,
  no verdict is picked anywhere in this note.
- **Novel**: net-new to the corpus:
  1. **Ambient team context as a silent mis-attribution footgun with a
     documented-but-unenforced remedy** (Claims 1–2) — persisted CLI state
     decides where evals/scans land, the vendor's only verification is an
     advisory `whoami` with no machine-readable contract and no gate. The
     corpus has credential-scoping rules (declare, don't infer) but no prior
     instance of *post-credential* ambient state deciding artifact placement on
     a shared runner.
  2. **The full seven-permission RBAC inventory** (Claim 5), verbatim, with the
     `Run Scans` ⊃ "view results" bundling made explicit — the corpus only held
     three of the seven strings, quoted as cross-page context inside the audit
     note. This is now the citable permission-model artifact for promptfoo
     Enterprise.
  3. **The two-level tenancy matrix** (Claim 3): org = credential-defined,
     team = per-org remembered ambient state, resources = team-scoped — the
     compositional rule a CI service account must satisfy, stated as the
     vendor's own three-bullet contract.
  4. **Role assignment as a membership-row property** (Claim 6) for both human
     and machine identities, and the bounded-resource question it opens
     (Claim 8).

## Guide Impact

- **Chapter 06 (security and trust)** — add a concrete pre-flight pattern to
  the credential/CI-CD-identity guidance: for any automated promptfoo Enterprise
  run that shares results or runs scans, the job must (a) pin team context
  explicitly (`promptfoo auth teams set "<team>"` in the bootstrap step) and
  (b) assert `promptfoo auth whoami` output before the publishing step — cite
  Claims 1–2 and the vendor's own tip as evidence that the platform treats
  this as a user responsibility, not an enforced invariant. State the tenancy
  split alongside it (Claim 3): the API key fixes the organization, local
  state fixes the team, so key custody governs *cross-tenant* exposure while
  context hygiene governs *intra-org attribution* — two different controls
  that must both be right.
- **Chapter 06 (least privilege for machine identities)** — use the verbatim
  seven-permission inventory (Claim 5) as the worked example of separable
  execution vs. mutation: a scan-runner service account should hold `Run
  Scans` without `Manage Results`, so CI output cannot edit or delete
  evaluations/issues; reviewers hold `View Results`; nothing needs
  `Administrator`. Pair with the sibling service-accounts note's inert-until-
  bound Claim 3 for the binding step, and the admin-gate provisioning
  dependency (Claim 4). Caveat to carry: no role templates or permission→role
  mapping are documented (Claim 7), so this is a *model* to request/verify in
  the tenant, not a documented configuration recipe.
- **Chapter 05 (LLM ops reliability)** — one targeted addition: ambient
  context as a reliability class of its own for shared runners — a run that
  succeeds but lands in the wrong team is an operational failure with no error
  signal (Claims 1–2). Fold `whoami` assertion into the guide's existing
  "declare, don't infer" family of job-state checks.
- **Do not** infer CI-gating guidance from this page: no thresholds, webhooks,
  status checks, or pass/fail semantics are documented (Claim 7). The
  gating-relevant material the corpus *can* cite lives in
  `docs-promptfoo-enterprise-findings-reports.md` (its Claim 11's explicit
  non-claim) and `docs-promptfoo-enterprise-webhooks.md` (its Claim 1's event
  set) — this note only supplies the permission vocabulary a gate would run
  under.

## Extraction Notes

- Deep-read of the full page (single fetch of the rendered page, 2026-10-16);
  **2 of 5** permitted sibling pages followed —
  `/docs/enterprise/service-accounts/` fetched directly (wording comparison for
  Claim 4, artifacts section), `/docs/enterprise/authentication/` read via its
  dedicated corpus note for the overlapping CLI-context material. All claims
  are sourced from the teams page itself unless explicitly attributed.
- `miner-related-notes.md` (repo root) was read before writing
  Cross-References; all ten listed candidates are cited or dismissed by name
  above. It is **not** committed with this PR.
- **Quotes** were copied character-for-character from the rendered page's
  visible text (bold markers in the permission/isolation bullets are part of
  the rendered string and are preserved); no quote splices two non-adjacent
  sentences. The Claim 8 quote is a permission-string fragment used as evidence
  of the enumeration narrowness — the narrowness itself is a two-list
  comparison, stated as our reading under Our assessment.
- **Absence claims (Claims 7, 8) are deliberate**, verified by full-page read,
  not inferred — and bounded per corpus convention: undocumented ≠
  nonexistent. The Prospector's scope limit ("no config snippets, no API
  endpoints, no quotas, no rate limits, no error codes, no failure modes; do
  not over-claim operational guarantees") was honored: the note extracts CLI
  state semantics, isolation rules, and permission vocabulary only, and
  explicitly declines to claim CI-gating behavior.
- **No contradiction issue filed** (see Cross-References → Contradicts): the
  two candidate tensions were examined and fall under MINER §4a's
  "when NOT to file" (framing variance; documented gaps without opposing
  claims). Open `contradiction`-labeled issues were checked for promptfoo
  teams/RBAC coverage before concluding.
- `date_published` is the page's "Last updated" stamp (renovate bot bump), not
  an editorial publication date — the page carries none.
- Not code-verifiable: Enterprise-gated hosted feature; no attempt was made to
  treat open-source repository code as a check on these claims.
- `confidence_overall: emerging` — the documented contract (commands,
  permission strings, isolation bullets) is the vendor's own specification and
  is settled as such, but the enforcement surface behind it is unobservable
  without a tenant; matches the cluster convention (5 of 6 sibling Enterprise
  notes are `emerging`, the pure-procedure service-accounts note excepted).
- Duplicate check: no existing source note for this URL (grep for
  `enterprise/teams` across `source-notes/` and `guide/` hits only
  cross-references in the authentication and audit-logging notes, both of which
  defer here for the full extraction).
- Registry files (`registry/sources.json`, `registry/claims-index.json`) were
  not edited (derived indexes, rebuilt after merge).
