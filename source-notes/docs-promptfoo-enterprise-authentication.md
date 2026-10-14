---
source_url: https://www.promptfoo.dev/docs/enterprise/authentication
source_type: docs
title: "Promptfoo Enterprise: Authentication — Vendor-Provisioned SSO, the CLI Credential Flow, and the Org/Team Scoping Behind `--share`"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-14
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: emerging
issue: "#1590"
---

# Promptfoo Enterprise: Authentication

> The identity half of promptfoo's eval-artifact trust boundary: how a hosted
> eval tenant authenticates (basic/magic-link at `auth.promptfoo.app`, SSO via
> SAML 2.0/OIDC configured *by vendor support, not self-service*), how the CLI
> binds to an organization via `promptfoo auth login --api-key`, and why
> `promptfoo eval --share` / `promptfoo share` land in an org-scoped,
> team-scoped destination rather than the public web — eval results stay local
> until that explicit upload.

## Source Context

- **Type**: docs (vendor product documentation — Promptfoo Enterprise
  "Enterprise > Authentication" page). Page header carries the gating notice
  "This feature requires Promptfoo Enterprise." Page footer: "Last updated on
  **Oct 14, 2026** by **renovate\[bot\]**" (a dependency bump, not an editorial
  change — `date_published` above is that last-updated stamp; the page publishes
  no original publication date).
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor,
  documenting its own Enterprise control plane. Authoritative *as a
  specification* of the login/CLI/team flow — the commands, endpoint host, and
  scoping statements below are the vendor's own contract and are
  string-checkable by anyone with an Enterprise tenant. It is not measurement:
  no config surface, no token semantics, no failure modes, and nothing on the
  page is verifiable without a paid Enterprise tenant (the page is not
  describing open-source code paths).
- **Scope**: Covers the auth methods offered on the hosted Enterprise app
  (basic + magic link + SSO), the CLI login procedure, the local-until-shared
  default, the org-scoping of shared results, and the multi-team CLI context
  commands. Does **not** cover: any SSO configuration parameters (client
  ID/secret, discovery URL, attribute/claim mappings, redirect URLs, token
  lifetimes), self-service IdP setup, SCIM/JIT provisioning, RBAC role
  definitions, env-var credential configuration, key rotation, session/expiry
  semantics, or what any of this looks like in the audit log (that half is
  `docs-promptfoo-enterprise-audit-logging.md`, issue #1589).
- **Sibling/linked pages followed** (3 of the 5-permitted budget), used for
  context only; every claim below is sourced from the authentication page
  itself unless explicitly attributed: `/docs/usage/sharing/` (what the share
  upload carries and the `--host` / `--auth-header-name` variants),
  `/docs/enterprise/teams/` (RBAC vocabulary, `promptfoo auth whoami`, team
  isolation per organization), `/docs/enterprise/sso/` (the on-prem/FusionAuth
  IdP path the hosted page defers customer-hosted deployments to).

## Extracted Claims

### Claim 1: Enterprise SSO supports SAML 2.0 and OIDC, but on the hosted product the IdP configuration is vendor-provisioned — customers "reach out to the support team," and the auth endpoint is `auth.promptfoo.app`
- **Evidence**: The "Setting Up SSO" section is a single sentence pair: protocol
  names plus a support-ticket instruction. No form, no self-service console, no
  documented parameters.
- **Confidence**: settled (documented product behavior — the *procedure* is
  unambiguous even though the configuration itself is unpublished)
- **Quote**: "Promptfoo Enterprise supports both basic authentication and SSO
  through SAML 2.0 and OIDC. To configure SSO with Promptfoo Enterprise, reach
  out to the support team with your IdP information and the Promptfoo team will
  configure it. The authentication endpoint is `auth.promptfoo.app`."
- **Our assessment**: Buy it as a statement of process, and read it as a
  control-plane limitation rather than a technical recipe: SSO enablement for
  the hosted product is a vendor-side change gated on a support interaction, so
  IdP cutover/rollback timelines are partly the vendor's, not yours. The page's
  opening deferral ("For customer-hosted deployments, see On-Prem SSO for
  identity-provider setup and team/role mapping") is the tell that the
  self-service path exists only for on-prem, where it runs on FusionAuth
  (per the followed `/docs/enterprise/sso/` page) — two different auth stacks
  under one "SSO" heading. Nothing configurable to extract from the hosted half;
  we record the boundary, not a setup guide.

### Claim 2: The authentication page documents no SSO configuration surface at all — no client ID/secret, no discovery URL, no claim mappings, no token lifetimes, no RBAC roles
- **Evidence**: Negative finding from a full read of the page: the SSO section
  is Claim 1's sentence, RBAC is deferred ("Users, teams, and roles will be
  created in the Organization Settings of the Promptfoo Enterprise application,
  which is detailed further in the Teams documentation"), and the only
  operational detail of any kind is the magic-link spam-folder note.
- **Confidence**: settled (the absence is directly checkable on the page)
- **Quote**: "Users, teams, and roles will be created in the Organization
  Settings of the Promptfoo Enterprise application, which is detailed further in
  the [Teams documentation](/docs/enterprise/teams/)."
- **Our assessment**: This is the page's most important property for the guide:
  the docs answer "how do I get in" but not "how is access enforced." Anything
  about session duration, credential rotation, or what an SSO login asserts
  about the user is *unknown rather than absent* — the same distinction the
  audit-logging note draws for its event taxonomy. Do not let this note's
  existence imply the corpus knows promptfoo's token semantics; it does not.

### Claim 3: Basic auth on the hosted product is org-provisioned — the global admin gets an email invite at `auth.promptfoo.app`, and magic-link login is the documented alternative
- **Evidence**: "Basic Authentication" section: org-creation email flow plus a
  click-path for magic link, including the only troubleshooting line on the page.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can also authenticate into the application using a magic
  link. To do this, navigate to `auth.promptfoo.app` and click the \"Login with
  a magic link\" button. You will receive an email with a link to log in. If you
  do not receive an email, please be sure to check your spam folder."
- **Our assessment**: Standard passwordless-then-email onboarding. Two small
  operational notes worth keeping: (a) magic link means email delivery is on the
  login critical path (the spam-folder line is the vendor acknowledging that);
  (b) the invite is addressed to a "global admin," i.e. the org's first identity
  is provisioned out-of-band by the vendor, which is consistent with Claim 1's
  vendor-operated control plane.

### Claim 4: CLI authentication is a copy-a-command flow from the app's profile ("CLI Login Information"), and its stated purpose is to let the authenticated CLI share locally-run eval results
- **Evidence**: Four-step "Authenticating Into the CLI" procedure with two
  screenshots; the vendor states the enabling outcome directly.
- **Confidence**: settled (documented procedure)
- **Quote**: "Copy the first command and run in your CLI. Your CLI will then be
  authenticated to Promptfoo Enterprise, allowing you to share eval results run
  locally."
- **Our assessment**: Buy it. Note what the credential is *for* on this page:
  the CLI login's documented reason to exist is egress of results (`--share` /
  `share`), not eval execution itself — local `promptfoo eval` needs no
  Enterprise login. That scopes the blast radius of a leaked CLI credential to
  the upload/tenant surface (subject to whatever else the key authorizes, which
  this page does not say). Contrast with the code-scanning CLI, which resolves
  auth by an explicit precedence chain including env var and GitHub OIDC
  (`docs-promptfoo-code-scan-cli.md` Claim 7) — no such precedence table is
  given here.

### Claim 5: Eval results are stored locally until explicitly shared — sharing is an opt-in upload, not a background sync
- **Evidence**: The step-4 tip block, stated as a product invariant for both new
  and migrated (former open-source) users.
- **Confidence**: settled (documented product behavior; corroborated by the
  Sharing page's payload description)
- **Quote**: "All of your evals are stored locally until you share them. If you
  were previously an open-source user, you can share your local evals to your
  Promptfoo Enterprise organization by running `promptfoo share`."
- **Our assessment**: Buy it, and it is the load-bearing sentence for the Ch06
  trust boundary: the default data-flow is *none* — eval snapshots (prompts,
  vars, outputs, traces — the payload list is enumerated verbatim in
  `docs-promptfoo-configuration-outputs.md` Claim 6) only leave the machine on a
  deliberate `share` command or `--share` flag. This is the identity-side
  counterpart to that note's payload-side rule; together they define where eval
  artifacts go and what they carry.

### Claim 6: Authenticated sharing is org-scoped — team-based sharing makes results "only visible to members of your organization rather than being publicly accessible"
- **Evidence**: The paragraph immediately after the CLI login steps ties the
  login to a visibility guarantee; the Sharing page (followed) corroborates with
  "Cloud sharing creates private links only visible to you and your organization"
  and "Enterprise users: Creates team-accessible links with role-based
  permissions."
- **Confidence**: settled (documented product behavior, two pages agree)
- **Quote**: "Authenticating with your organization's account enables
  team-based sharing, ensuring your evaluation results are only visible to
  members of your organization rather than being publicly accessible."
- **Our assessment**: Buy it — this is the security-relevant claim the
  Prospector flagged. The boundary is *organization* membership, with team
  granularity layered on by the Teams/RBAC surface (Claim 8-10 here and the
  Teams doc's role-based permissions). Practical corollary for the guide: the
  `--share` upload is not "to promptfoo the vendor's public gallery," but it is
  also not "stays in your CI workspace" — it crosses the machine boundary into
  a multi-tenant SaaS whose access control you configure in someone else's
  console (Claims 1-3). Eval snapshots can carry production-adjacent prompt and
  output data, so org-scoped ≠ harmless: offboarding, org membership, and key
  custody all become data-exposure levers.

### Claim 7: The team CLI surface is three commands — `promptfoo auth teams list | set | current` — and the team selection persists across CLI sessions
- **Evidence**: The "Working with Multiple Teams" section, with a command block
  per sub-step and the persistence statement in "Switching Teams."
- **Confidence**: settled (documented commands, directly checkable on any
  Enterprise tenant)
- **Quote**: "You can use the team name, slug, or ID. Your selection persists
  across CLI sessions."
- **Our assessment**: Buy it. Persistence across sessions is the
  double-edged operational detail: you don't have to re-select per invocation,
  but a stale team context silently determines where the next eval/scan lands
  (Claim 10) — a footgun on shared or long-lived runners. The Teams doc (followed)
  confirms the mirror-image hygiene rule: `promptfoo auth whoami` before
  important operations, and team selections are remembered *per organization*.

### Claim 8: The team list is scoped by the credential, not the machine — teams shown are "the teams accessible to your API key in its organization"
- **Evidence**: "Viewing Your Teams" section; the `●` current-team marker plus
  the API-key scoping statement.
- **Confidence**: settled (documented behavior)
- **Quote**: "This shows the teams accessible to your API key in its
  organization, with a marker (●) next to your current team."
- **Our assessment**: Buy it, and it is the precise mechanism behind the
  tenant-boundary claim: what a CLI session can see and do flows from the API
  key it holds. There is no documented per-machine account database involved —
  the credential *is* the tenancy context. This matters for CI: a pipeline's
  key decides which org's teams exist for it, so key custody = tenant
  membership.

### Claim 9: Switching organizations is done by presenting a different org's API key — `promptfoo auth login --api-key <apiKey>` — so the key's org defines the tenant boundary
- **Evidence**: The final sentence of "Switching Teams"; reinforced by the Teams
  doc's "Team Isolation" bullet ("API keys are scoped to one organization").
- **Confidence**: settled (documented behavior, two pages agree)
- **Quote**: "To switch organizations, run `promptfoo auth login --api-key
  <apiKey>` with a key from the organization you want to use."
- **Our assessment**: Buy it. Tenant boundary is credential-defined and
  re-establishable on demand: anyone holding a key from org B can point the same
  CLI at org B. That is the correct multi-tenant design, and it sharpens the
  operational rule for the guide: rotate/revoke Enterprise API keys as an
  access-control action (they are the org boundary), and treat "which key is
  logged in" as the first thing to check when results appear in the wrong
  tenant. The page documents no key-rotation procedure (Claim 2).

### Claim 10: Team context is a scoping input to execution, not display state — all subsequent operations, including red-team scans, run under the selected team until it is switched
- **Evidence**: The closing statement of "Checking Current Team," explicitly
  enumerating operations.
- **Confidence**: settled (documented behavior)
- **Quote**: "All operations (evaluations, red team scans, etc.) will use this
  team context until you switch to a different team."
- **Our assessment**: Buy it — this is what elevates `auth teams set` from a
  convenience to a governance control: the team selection determines where eval
  results and red-team artifacts are *created*, which in turn determines who can
  see them (Claim 6) and which RBAC roles apply (Teams doc's permission list).
  Multi-team orgs running shared automation must therefore pin team context as
  deliberately as they pin the API key, or scans silently land in a default
  team. The Teams doc adds the explicit advisory: verify with
  `promptfoo auth whoami` "before sharing evaluation results or running scans."

## Concrete Artifacts

*(Source: the authentication page's "Working with Multiple Teams" section,
rendered as displayed — the plain-text extraction of the page collapses the
newline inside each code block, e.g. `# List all teams you have access
topromptfoo auth teams list`; comment and command are separate lines on the
page.)*

```
# List all teams you have access to
promptfoo auth teams list

# Switch to a different team
promptfoo auth teams set "Data Science"

# View your active team
promptfoo auth teams current
```

CLI login procedure (page's step list, condensed to its commands — the page
itself shows the command only inside screenshots "CLI Login Information" /
"CLI Login Command"):

```
# in the Promptfoo Enterprise app: profile → "CLI Login Information" → copy first command
<vendor-generated login command>

# afterwards
promptfoo eval --share     # or: promptfoo share
```

Org switch (page, "Switching Teams"):

```
promptfoo auth login --api-key <apiKey>
```

Tenant/scoping facts stated verbatim on the page:

- Auth endpoint: `auth.promptfoo.app`
- "All of your evals are stored locally until you share them."
- "This shows the teams accessible to your API key in its organization, with a
  marker (●) next to your current team."
- "All operations (evaluations, red team scans, etc.) will use this team
  context until you switch to a different team."

Context from followed sub-pages (attributed, not claims of this page):

- `/docs/usage/sharing/` — Enterprise share login variant
  (`promptfoo auth login --host https://your-company.promptfoo.app -k YOUR_API_KEY`,
  plus `--auth-header-name X-Promptfoo-Api-Key` for gateways that reserve
  `Authorization`), and the feature list "Team-based access controls /
  Role-based permissions for shared evals / SSO integration (SAML 2.0 and
  OIDC)".
- `/docs/enterprise/teams/` — `promptfoo auth whoami` (verify org + team before
  sharing/scanning), "API keys are scoped to one organization," and the
  seven-permission RBAC vocabulary (Administrator, View/Manage Configurations,
  Run Scans, Manage Targets, View/Manage Results).

## Cross-References

**Candidates from `miner-related-notes.md`** (read before writing this section;
every listed path is cited or dismissed by name):

- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — **dismissed as
  a substantive overlap**: findings disposition/export surface. It touches the
  same primitive only in passing — its **Claim 10** names "shareable URLs via
  `promptfoo share`" as part of the read-only findings programmatic surface —
  but carries no authentication, tenant, or team-scoping content.
- `source-notes/docs-promptfoo-enterprise-audit-logging.md` — **cited**
  (Extends — see below).
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch TPM/RPM
  rate-limit accounting for `POST /v1/batches`; no auth-tenant content.
- `source-notes/docs-langfuse-mcp-server.md` — **dismissed**: Langfuse docs MCP
  server, unauthenticated public endpoint; unrelated vendor surface.
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — **dismissed**:
  runtime guardrail evaluate contract. Its **Claim 1** does involve a
  `PROMPTFOO_API_KEY` Bearer header, but that is guardrail-API authorization,
  not login/tenant/team scoping; no overlap with this page's claims.
- `source-notes/blog-pagerduty-sre-agent-triage.md` — **dismissed**:
  AI-incident triage via an SRE Agent; no auth or eval-artifact egress content.
- `source-notes/docs-promptfoo-pi-scorer.md` — **dismissed**: third-party
  scoring-model grader using `WITHPI_API_KEY`; unrelated credential.
- `source-notes/docs-google-sre-eliminating-toil.md` — **dismissed**: toil
  characterization and measurement; unrelated.
- `source-notes/docs-google-sre-reliable-product-launches.md` — **dismissed**:
  launch-coordination discipline; unrelated.
- `source-notes/docs-google-sre-team-lifecycles.md` — **dismissed**: SRE team
  org/lifecycles (note: "team" here means an SRE org unit, not a promptfoo
  tenant team — no overlap).

Additional cross-references found by searching `source-notes/` (the Prospector's
overlap list): `docs-promptfoo-configuration-outputs.md`,
`docs-promptfoo-code-scan-cli.md`, `docs-litellm-gateway-auth-reference.md` —
handled below.

**Primary cross-references (verified per MINER §4b — cited claims re-read in the
source notes before writing):**

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 6** (the
    share/export paths carry an explicit "do not put secrets in shareable
    inputs" rule, and the Sharing page's payload list names prompts, vars,
    outputs, traces, metadata, provider config fields) — this page supplies the
    *identity/tenant* half of the same trust boundary: where that payload goes
    (org- and team-scoped destination, Claim 6 here) and what keeps it there
    (credential-selected org, Claim 9 here). The two notes are the egress rule
    and the egress destination, respectively. (Verified: claim heading and
    quotes re-read in that note.)
- **Extends**:
  - `source-notes/docs-promptfoo-enterprise-audit-logging.md` **Claim 4**
    ("`login` is documented as recording *successful* authentication only") —
    that note already anticipated this page, writing that "the Enterprise
    authentication surface is much richer than one event —
    `site/docs/enterprise/authentication.md` documents basic auth plus SSO via
    SAML 2.0 and OIDC, a magic-link login, and a CLI login flow — and none of
    those paths' events appear in the taxonomy." This note is the extraction of
    that deferred surface: Claims 1, 3, and 4 here are exactly the auth paths
    whose events the audit log lacks. Read together: this page says *how* you
    authenticate, that page says the audit log records only that a session was
    established (successful login), never how. (Verified: claim heading and
    quote re-read.)
  - `source-notes/docs-promptfoo-code-scan-cli.md` **Claim 7** (auth precedence
    chain `--api-key` → `PROMPTFOO_API_KEY` → `promptfoo auth login` → GitHub
    OIDC, CI-oriented) — this page is the human/Enterprise-tenant side of the
    same CLI credential story: no precedence table, no env-var path, purpose
    scoped to sharing (Claim 4 here). Together they show promptfoo's CLI auth is
    surface-dependent: code scanning documents machine credentials, Enterprise
    documents an interactive app-driven login. (Verified: claim heading and
    quote re-read.)
- **Contradicts**: **None identified, and no contradiction issue filed.**
  Checked against `CONTRADICTIONS.md` (format-only file; no `C-NNN` entries) and
  open `contradiction`-labeled issues (#1150, #1307, #1322, #1338, #1352,
  #1408, #1461, #1462, #1486, #1514, #1517, #1534, #1548, #1550, #1562, #1565,
  #1591, #1593, #1597, #1633) — none touch promptfoo authentication, tenant, or
  team scoping. The one candidate tension was checked rather than assumed: the
  audit-logging note's finding that no auth-path events are auditable (its
  Claim 4) is an *audibility gap* in a different feature, not an opposing claim
  about how authentication works — this page asserts nothing about auditing, so
  the two do not conflict. No verdict picked per MINER §4a.
- **Novel**: the credential-defined tenant boundary for a hosted eval platform
  (Claims 8-10): the API key picks the organization, the session picks the
  team, and team context is an execution-scoping input for evals *and red-team
  scans* — multi-tenant eval governance expressed as three CLI commands. Also
  novel to the corpus: the vendor-provisioned (non-self-service) SSO control
  plane as an operational dependency (Claim 1), and the explicit statement that
  eval artifacts are local until an authenticated, org-scoped upload (Claims
  5-6). The nearest analogue in the corpus,
  `docs-litellm-gateway-auth-reference.md` (a *different product* — self-hosted
  gateway auth: API-key/team/org resolution over MCP/A2A routes), covers
  inbound gateway authorization rather than eval-artifact tenancy; it is a
  thematic parallel, not corroboration, and is not cited as agreement.

## Guide Impact

- **Chapter 06 (security and trust)** — extend the existing share/export trust
  boundary (already recommended from `docs-promptfoo-configuration-outputs.md`
  Claim 6: "do not put secrets in shareable inputs") with the destination side:
  `promptfoo eval --share` / `promptfoo share` uploads eval snapshots to an
  **organization- and team-scoped** Enterprise destination, gated on an
  interactive CLI login whose documented purpose is that upload; results are
  local until then. Add the operational corollary: the tenant boundary is the
  API key (`promptfoo auth login --api-key`), so key custody and revocation are
  access-control actions for eval data, and `promptfoo auth teams set` should be
  pinned/verified (via the Teams doc's `promptfoo auth whoami`) before sharing
  or scanning on shared runners.
- **Chapter 06 (supply/control-plane dependencies)** — record vendor-provisioned
  SSO as an operational dependency for hosted Enterprise: SAML 2.0/OIDC enable
  is a support-mediated vendor change (Claim 1), and the hosted page publishes
  no IdP parameters, token lifetimes, or role definitions (Claim 2) — so an
  evaluator's SSO/offboarding guarantees on this product are contractual, not
  configuration you can inspect. Do not let Ch06 imply a self-service SSO
  recipe exists for the hosted tier; the self-service path is on-prem only
  (FusionAuth, per `/docs/enterprise/sso/`).
- **No Ch05 change recommended**: nothing here bears on eval-run reliability;
  the Prospector's Ch05 hook did not survive deep reading.

## Extraction Notes

- Deep-read of the full page; **3 of 5** permitted sub-pages followed and read
  in full (`/docs/usage/sharing/`, `/docs/enterprise/teams/`,
  `/docs/enterprise/sso/`), used only for context and explicitly attributed
  where quoted — no claim above is sourced from a sub-page without saying so.
- **Text-extraction artifact**: the plain-text fetch of the page collapses the
  newline inside each team-command code block (comment and command run together
  as `... access topromptfoo auth teams list`). Concrete Artifacts renders them
  as displayed on the rendered page; all prose quotes were taken from the
  rendered page's visible text and copied character-for-character.
- **Absence claims are deliberate** (Claim 2): the SSO-config/token-lifetime/RBAC
  gaps were verified by reading the whole page, not inferred. Per the
  Prospector's caveat, nothing in this note over-claims SSO configuration detail
  the page does not contain.
- `date_published` is the page's "Last updated" stamp (renovate bot bump), not
  an editorial publication date — the page carries none.
- Not code-verifiable: the page describes an Enterprise-gated hosted feature;
  no attempt was made to treat open-source repository code as a check on these
  claims (the hosted auth plane is not in the OSS product).
- Duplicate check: no existing source note for this URL (grep for
  `enterprise/authentication` across `source-notes/` and `guide/` hits only
  `docs-promptfoo-enterprise-audit-logging.md`, which anticipates and defers to
  this note — cited under Extends).
- `miner-related-notes.md` (repo root) was read before writing
  Cross-References and is **not** committed with this PR.
