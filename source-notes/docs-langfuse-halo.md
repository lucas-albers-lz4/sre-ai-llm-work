---
source_url: https://langfuse.com/docs/halo
source_type: docs
title: "Halo — Langfuse Assistant"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: n.d. (vendor docs; Halo public beta announced 2026-06-19)
date_extracted: 2026-10-17
last_checked: 2026-10-17
status: current
confidence_overall: emerging
issue: "#1767"
---

# Halo — Langfuse Assistant

> Vendor documentation for a shipped in-app AI assistant over production
> observability data whose write side is kept under control by a
> permission-scoped human-approval gate: Halo pauses before changing data or
> configuration, approvals inherit only the signed-in user's existing project
> permissions ("Approval does not grant additional access"), "Always approve"
> lasts only for the current conversation, and large observation sets are
> processed by code in a sandbox rather than unbounded tool calls.

## Source Context

- **Type**: docs (vendor product documentation — feature page for a public-beta
  feature, with a substantive self-hosted configuration sub-page)
- **Author credibility**: Langfuse is a production LLM-observability vendor
  documenting its own shipped surface. Claims about prerequisites, approval
  semantics, env vars, and data routing are authoritative statements of design
  intent and configuration (settled as facts about the docs), but there are no
  metrics, incident reports, or third-party validation on the page — every
  effectiveness/security claim is vendor assertion and is graded accordingly.
- **Scope**: Covers what Halo does, its approval model, background runs,
  conversation state, data-handling/privacy model, and limitations; the linked
  self-hosted setup page covers the full prerequisite chain (instance AI model,
  worker queue consumer, optional AWS Lambda MicroVM sandbox, IAM, networking)
  and self-tracing. Per the Prospector's triage, the plan-availability table
  (Hobby/Core/Pro/Enterprise) and the feedback/thumbs-up sections were skipped
  as noise. Does NOT cover pricing beyond the changelog's "free during the
  Beta", tool schemas (deferred to the MCP Reference), or any usage metrics.
- **Sub-pages followed** (MINER.md §1, 4 of the 5-link budget):
  1. `/self-hosting/configuration/halo` — the self-hosted prerequisite chain,
     model/provider config, sandbox build/IAM/network isolation, activation,
     deployment recipes, self-tracing. Substantive; contributes Claims 3, 4, 6,
     7, 8, 10 and most Concrete Artifacts.
  2. `/security/ai-features` — org-level opt-in, Cloud Bedrock data handling,
     self-hosted responsibility split, tracing toggle. Substantive; contributes
     Claims 5 and 11.
  3. `/docs/api-and-data-platform/features/mcp-server` — the authenticated MCP
     tool surface Halo reuses (already covered by
     `docs-langfuse-mcp-server.md`); read to verify the Halo/MCP relationship
     and the `LANGFUSE_MCP_ALLOWED_HOSTS` 403 note.
  4. `/changelog/2026-06-19-langfuse-assistant-public-beta` — release date and
     launch state (Cloud-only at launch, free during Beta). Context only.
  Not followed: the FAQ troubleshooting page and the feedback discussion
  (support/community surfaces, no extractable claims).

## Extracted Claims

### Claim 1: Halo is the same Langfuse MCP project-tool surface that external coding agents use, wrapped in the Langfuse UI with UI-context injection, background execution, notifications, and approvals
- **Evidence**: The "How it works" section states Halo uses the same MCP
  project tools plus documentation search and sandboxed code execution, and
  lists exactly what the in-app wrapper adds; the intro says it "brings the
  same Langfuse project tools available to external coding agents into the
  Langfuse UI."
- **Confidence**: settled (factual description of a shipped surface)
- **Quote**: "Halo uses the same Langfuse MCP server project tools that
  external agents can connect to, together with documentation search and
  sandboxed code execution. The in-app experience adds your current UI context
  (the trace, observation, session, or dashboard you are viewing, plus your
  name, browser language, and timezone), background execution, notifications,
  and approvals in Langfuse."
- **Our assessment**: The load-bearing architecture fact: the vendor did not
  build a second tool stack for its in-app agent — it wraps its own public
  data-platform MCP server (documented in `docs-langfuse-mcp-server.md`,
  Claim 8) in a first-party UI shell. The UI-context injection (current
  trace/session/dashboard + user name, locale, timezone) is the concrete
  "screen context" the roadmap promised (see Cross-References). For SREs the
  transferable unit is: one tool surface, two consumers (external agents via
  MCP, in-product agent via the same tools), with the *wrapper* supplying the
  safety policy.

### Claim 2: The approval gate pauses mutations, scopes them to the signed-in user's existing project permissions, and grants no extra access; "Always approve" expires with the conversation
- **Evidence**: The "Action approvals" section — three sentences that define
  the entire write-side authorization model.
- **Confidence**: emerging (design intent of a beta feature; no validation
  that the gate reliably intercepts every mutation path)
- **Quote**: "Halo pauses for your approval before changing data or
  configuration. Always approve lets a tool run without asking again in the
  current conversation. Halo is limited to your existing permissions in the
  current project. Approval does not grant additional access."
- **Our assessment**: This is the most transferable pattern in the source and
  the reason this page is worth a note despite low novelty scoring. Three
  deliberate properties: (i) default-deny on mutations — reads proceed, writes
  stop for a human; (ii) approvals are *permission-preserving* — the approval
  is an authorization check against an existing RBAC binding, not a grant, so
  an approver cannot escalate; (iii) the "always" escape hatch is
  conversation-scoped, so trust does not persist across sessions. This is a
  vendor implementation of the posture Google's Prodcast S4E9 already
  prescribes (deny world-mutating actions, require explicit human permission)
  and pairs well with the MCP server's contrasting default (write tools on,
  restrict via client allowlist — `docs-langfuse-mcp-server.md`, Claim 9).
  Note the tension is *not* a contradiction: that claim is about the raw MCP
  endpoint's defaults for arbitrary external clients, this is about the
  vendor's own wrapper over it — see Cross-References.

### Claim 3: Large observation sets are processed with code in a sandbox instead of loading every item into model context; without a sandbox those tools are disabled entirely
- **Evidence**: The capability bullet on the main page plus the self-hosted
  setup page's setup-choice table and sandbox section.
- **Confidence**: settled (capability/config description)
- **Quote**: "We recommend the AWS Lambda MicroVM sandbox. It enables file and
  code-execution tools, which let Halo process large sets of traces and
  observations with code instead of loading every item into the model context."
- **Our assessment**: A concrete answer to the "unbounded tool calls over
  telemetry" cost problem: move the fan-out into sandboxed code (filter,
  cluster, aggregate) and give the model only the result. The degraded mode is
  explicit and worth recording — "Without a sandbox, file and code-execution
  tools are disabled" (self-hosted page), so non-AWS self-hosters silently lose
  the at-scale analysis capability. The vendor also states there is no
  non-AWS sandbox yet, which is a real platform-lock-in consequence of the
  recommended architecture.

### Claim 4: Self-hosting Halo has a three-link prerequisite chain — public beta from `>=v4.28.0` (not SemVer-covered), an instance-wide Langfuse AI model configured on both web and worker, and a worker queue consumer
- **Evidence**: The main page's self-hosted callout plus the self-hosted
  page's requirements section and activation step (`LANGFUSE_IN_APP_AGENT_ENABLED`
  on workers, which "consume Halo's run queue").
- **Confidence**: settled (version facts and env-var contract as of extraction;
  the page itself warns config "may change between releases")
- **Quote**: "Halo is in public beta from version >=v4.28.0 and needs an
  instance-wide Langfuse AI model and a worker queue consumer."
- **Our assessment**: The operational cost the Prospector asked about,
  confirmed in full. Three implications: (1) one instance-wide provider/model
  for all AI features — `LANGFUSE_AI_PROVIDER` + `LANGFUSE_AI_MODEL` set on
  *both* web and worker, with an optional `LANGFUSE_AI_SMALL_MODEL` for
  conversation titles (if unset you pay primary-model price for titles);
  (2) workers with `LANGFUSE_IN_APP_AGENT_ENABLED=true` become Halo executors,
  so queue capacity is taken from ingestion workers — "Leave it unset on
  ingestion-only workers" is explicit capacity hygiene; (3) beta status means
  no SemVer guarantee — operators must track OSS release notes for config
  drift. The Helm chart (`langfuse.aiFeatures`, chart `v2.1.0+`) and Terraform
  module (`>=1.2.0`) are the blessed deployment paths.

### Claim 5: The data-handling model routes Cloud requests through Langfuse-managed Amazon Bedrock in the customer's data region, self-hosted requests through the operator-configured instance model, and scopes access to the signed-in user and current project
- **Evidence**: The "Data privacy and security" section plus the AI-features
  security page's Data Privacy section (Bedrock zero-retention claims, "You
  are responsible for that provider's data handling" on self-hosted).
- **Confidence**: emerging (vendor security assertion; routing/scoping
  statements are design facts, the downstream provider guarantees are as
  relayed from AWS docs, not independently verified here)
- **Quote**: "On Langfuse Cloud, model requests use Langfuse-managed Amazon
  Bedrock in your Langfuse data region. On self-hosted deployments, requests
  use the instance Langfuse AI model you configure."
- **Our assessment**: The privacy story has three distinct legs worth keeping
  separate in Ch06: *where prompts go* (Bedrock in-region on Cloud; your
  provider on self-hosted — where the AI-features page explicitly shifts
  responsibility: "You are responsible for that provider's data handling"),
  *who the agent can see* ("Access is scoped to the signed-in user and current
  project" — the agent inherits the session's RBAC rather than a service
  principal), and *whether Langfuse records the AI traffic* (AI feature
  tracing toggle, Claim 11). Cloud's Bedrock-only model is a meaningful
  simplification: no third-party model API relationship, no training-on-your-data
  surface, HIPAA/SOC2/ISO27001 relayed from AWS.

### Claim 6: Halo runs are durable jobs — web enqueues, worker claims and executes — with runs surviving the browser and conversations persisted per user and project
- **Evidence**: The "Background runs" and "Conversation history" sections on
  the main page plus the infrastructure overview table on the self-hosted page.
- **Confidence**: settled (architecture description)
- **Quote**: "Halo runs are durable jobs. The web service admits and enqueues
  them, and the worker claims and executes them."
- **Our assessment**: The async-queue pattern applied to an interactive
  assistant: the browser session is decoupled from execution, so a long
  at-scale analysis (Claim 3's clustered error investigation) outlives the tab
  and the user gets notified on completion. Per-user/per-project conversation
  persistence means conversational state is tenancy-scoped, consistent with
  the per-project MCP key model (`docs-langfuse-mcp-server.md`, Claim 8).
  For the guide this is the difference between "chatbot bolted onto a page"
  and "run queue with a chat front end" — the latter is what production agent
  workloads actually need.

### Claim 7: The recommended sandbox is network-isolated by default but becomes internet-reachable unless an egress network connector is explicitly attached, and the execution role must hold no Langfuse data access
- **Evidence**: The self-hosted page's IAM-and-network-isolation subsection —
  deny-all security group, private subnets, and two explicit warnings (egress
  connector required for production isolation; execution-role restriction).
- **Confidence**: emerging (documented mechanism; no adversarial validation of
  the sandbox boundary in the source)
- **Quote**: "Production isolation requires the egress network connector.
  Without it, AWS attaches its default INTERNET_EGRESS connector and sandboxed
  code can reach the public internet. An invalid connector ARN fails the
  MicroVM launch."
- **Our assessment**: The sharpest security detail on either page. The default
  AWS behavior silently defeats the "deny-all security group" story — a
  sandbox that runs *user-prompted* code (traces contain untrusted data, a
  known prompt-injection surface) with default internet egress is an exfiltration
  path. Langfuse documents both mitigations: attach the egress connector, and
  "User-provided sandbox code runs as the execution role. Do not grant this
  role access to Langfuse databases, storage, or secrets." That second rule is
  classic least-privilege separation — the code that analyzes telemetry must
  not hold credentials for the telemetry store. Both belong in Ch06 as a
  worked example of sandboxing agent code execution.

### Claim 8: Operators can trace the assistant itself by pointing `LANGFUSE_AI_FEATURES_PROJECT_ID` at a dedicated project, which makes Halo's prompts, tool calls, and model output readable by anyone with access to that project
- **Evidence**: The "Trace Halo in your own instance" section with its
  adjacent warning callout, corroborated by the AI-features page.
- **Confidence**: settled (config contract plus explicit data-exposure warning)
- **Quote**: "Use a dedicated project. Halo traces contain prompts, tool
  calls, model output, and data read from other projects. Anyone with access
  to the target project can read that data."
- **Our assessment**: Observability of the observability assistant — the
  vendor dogfoods its own trace pipeline to record agent runs, and the
  recorder adds no egress: "Langfuse writes them through its internal
  ingestion path, so no API keys or outbound requests are required." The
  warning is the real lesson: agent traces are
  *aggregated sensitive data* — they carry whatever the assistant read from
  other projects — so the trace sink must be a dedicated project with tighter
  access than the source projects. Unset means nothing recorded
  (privacy default). This is a generalizable pattern: any AI-features telemetry sink
  needs its own access boundary, not "the team's shared project."

### Claim 9: The vendor explicitly advises verifying Halo's answers and reviewing proposed actions before approving them
- **Evidence**: The "Limitations" section — the only failure-mode content on
  the page.
- **Confidence**: settled (the vendor states it)
- **Quote**: "Halo can misunderstand a question or return incomplete results.
  Verify important answers and review proposed actions before approving them."
- **Our assessment**: The approval gate (Claim 2) is only as strong as the
  human at the button, and the vendor says so: the approver must actually
  review the proposed action, implying approval clicks can rubber-stamp. This
  is the standard automation-complacency hazard restated by the vendor
  itself — worth pairing with the guide's human-in-the-loop guidance. No
  metrics on how often Halo is wrong; graded as an honest limitation
  statement, not evidence of a defect rate.

### Claim 10: Halo's system prompt and tool loop are developed against Claude Opus 5; other models work but tool calling and instruction following may vary
- **Evidence**: The self-hosted page's model-configuration step, including the
  small-model recommendation.
- **Confidence**: settled (vendor statement of its own development target)
- **Quote**: "Halo's system prompt and tool loop are developed against it.
  Other models work, but tool calling and instruction following may vary."
- **Our assessment**: A candid admission that agent reliability is
  model-coupled: the approval-gate flow depends on the model actually
  invoking tools in the expected order, and the vendor only guarantees that
  for one model. Operators substituting a cheaper/self-hosted model take on
  tool-calling variance in a feature whose safety case is tool-call gating —
  the most consequential place for a tool-calling miss. The `LANGFUSE_AI_SMALL_MODEL`
  split (titles/summaries on a cheap model) is the right cost pattern:
  funnel-sensitive agentic loop on the strong model, prose on the small one.
  (Langfuse Cloud pairs Claude Opus 5 with Claude Haiku 4.5.)

### Claim 11: All Langfuse AI features are org-level opt-ins that admins/owners control, with AI feature tracing toggleable independently of the features themselves
- **Evidence**: The AI-features security page's Opt-in section, restated for
  Halo in the main page's privacy section.
- **Confidence**: settled (access-control description)
- **Quote**: "All AI-powered features require an opt-in; they are not enabled
  by default. The opt-in is managed at the organization level and can be
  changed by an admin or owner."
- **Our assessment**: The activation model is deny-by-default at the *org*
  boundary — a self-hosted operator can run Langfuse with zero AI features
  (and, per Claim 4, unset `LANGFUSE_IN_APP_AGENT_ENABLED` hides Halo even
  when AI Features is on). The separate tracing toggle ("Admins and owners can
  also separately enable or disable AI feature tracing for product and service
  improvement. This does not disable the AI features themselves.") keeps
  improvement-telemetry distinct from feature use — a data-governance split
  worth mirroring in any platform that ships built-in AI assistants.

## Concrete Artifacts

### Self-hosted prerequisite callout (verbatim, langfuse.com/docs/halo)
```
Self-hosted: Halo is in public beta from version >=v4.28.0 and needs an
instance-wide Langfuse AI model and a worker queue consumer.
```

### Approval / background / conversation sections (verbatim, langfuse.com/docs/halo — "Action approvals", "Background runs", "Conversation history")
```
Halo pauses for your approval before changing data or configuration. Always
approve lets a tool run without asking again in the current conversation.
Halo is limited to your existing permissions in the current project. Approval
does not grant additional access.

Runs continue independently of your browser, so you can keep using Langfuse or
start another conversation.

Halo conversations are saved per user and project so you can return to
previous conversations.
```

### Model configuration — Amazon Bedrock (verbatim bash, self-hosted setup page)
```bash
# Required for Amazon Bedrock
LANGFUSE_AI_PROVIDER=bedrock
LANGFUSE_AI_MODEL=eu.anthropic.claude-opus-5

# Optional
LANGFUSE_AI_SMALL_MODEL=eu.anthropic.claude-haiku-4-5-20251001-v1:0
LANGFUSE_AI_AWS_BEDROCK_REGION=eu-west-1
```
Note from the same page: "Bedrock authenticates through the AWS credential
chain rather than `LANGFUSE_AI_API_KEY`" and Langfuse should get invoke-only
permissions (`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`).

### Docker Compose activation (verbatim `.env`, self-hosted setup page)
```bash
LANGFUSE_AI_PROVIDER=<bedrock|anthropic|openai|vertex>
LANGFUSE_AI_MODEL=<model-id>
# Optional, a cheaper model for supplementary calls such as conversation titles
LANGFUSE_AI_SMALL_MODEL=<small-model-id>
# Required for Anthropic and OpenAI-compatible providers
LANGFUSE_AI_API_KEY=<api-key>

LANGFUSE_MCP_BASE_URL=http://langfuse-web:3000
LANGFUSE_MCP_ALLOWED_HOSTS=langfuse-web

LANGFUSE_IN_APP_AGENT_ENABLED=true
```
Related MCP reachability note (self-hosted setup page): the worker resolves
MCP via `LANGFUSE_MCP_BASE_URL` (else `NEXTAUTH_URL`) + `/api/public/mcp`, and
"A `403` response with `Invalid Host header` means the hostname is missing
from `LANGFUSE_MCP_ALLOWED_HOSTS`."

### Sandbox worker configuration (verbatim bash, self-hosted setup page)
```bash
LANGFUSE_IN_APP_AGENT_SANDBOX_PROVIDER=lambda-microvm
LANGFUSE_IN_APP_AGENT_SANDBOX_AWS_LAMBDA_MICROVM_IMAGE_IDENTIFIER=arn:aws:lambda:<region>:<account-id>:microvm-image:<image-name>
LANGFUSE_IN_APP_AGENT_SANDBOX_AWS_LAMBDA_MICROVM_EXECUTION_ROLE_ARN=arn:aws:iam::<account-id>:role/<execution-role>
LANGFUSE_IN_APP_AGENT_SANDBOX_AWS_LAMBDA_MICROVM_REGION=<region>
# Strongly recommended for production isolation
LANGFUSE_IN_APP_AGENT_SANDBOX_AWS_LAMBDA_MICROVM_EGRESS_NETWORK_CONNECTOR_ARN=arn:aws:lambda:<region>:<account-id>:network-connector:<egress-connector-name>
```
Sandbox resource table (self-hosted setup page): S3 artifact bucket; MicroVM
build role (Lambda `CreateMicrovmImage`); MicroVM execution role ("attach no
policies"); security group ("Configure no ingress or egress rules");
subnets ("Use private or unrouted subnets with no default route to the
internet"); connector operator role; egress network connector.

### Enable and verify (verbatim steps, self-hosted setup page)
```
1. Sign in as an organization owner or administrator.
2. Open organization Settings and enable AI Features.
3. Open Halo in a project.
4. Ask it to summarize a recent trace and confirm the run moves from queued
   to running to complete.
5. If you configured a sandbox, ask it to write a file.
```

### Infrastructure components (verbatim table rows, self-hosted setup page)
```
Langfuse Web      | Existing | Enqueues runs, hosts the MCP server, and uses the model for Ask AI and conversation titles
Langfuse Worker   | Existing | Executes Halo runs and, when configured, starts the sandbox
Langfuse AI model | New, required dependency | Serves model requests from web and worker
Execution sandbox | New, optional infrastructure | Isolates file and code execution from the worker
```

### Trace-the-assistant variable (self-hosted setup page)
```bash
LANGFUSE_AI_FEATURES_PROJECT_ID=<project-id>
```
Accompanying warning (verbatim): "Use a dedicated project. Halo traces
contain prompts, tool calls, model output, and data read from other projects.
Anyone with access to the target project can read that data."

## Cross-References

- **Corroborates**:
  - `docs-google-sre-prodcast-04-09-ai-agents.md` **Claim 3** ("The default
    guardrail is to deny agents any world-mutating action and require explicit
    human permission before any write — writes run in a sandbox, and anything
    that breaks the sandbox needs an additional check") — Halo is exactly that
    posture productized: mutations pause for explicit human permission
    (Claim 2 here) and code execution is sandboxed (Claims 3, 7 here). The
    Prodcast is practitioner prescription; Halo is vendor implementation over
    production telemetry — strongest corroboration pair for this note.
  - `docs-langfuse-glossary.md` **Claim 12** (Langfuse Assistant — "An
    in-product AI assistant, available in beta on Langfuse Cloud, for
    exploring project data and Langfuse workflows in plain language. It
    queries traces, observations, sessions, and metrics through the Langfuse
    MCP server, searches documentation, and proposes navigation actions that
    you confirm.") — the earlier glossary entry for the same feature before
    the "Halo" name landed in the docs; its "proposes navigation actions that
    you confirm" corroborates the confirmation-gated design, and the Halo page
    adds mutation approval, permission scoping, background runs, and the
    self-hosted chain the glossary lacks.
  - `blog-cncf-cluster-aware-ai-agent-argo-gitops.md` **Claim 3** ("start
    every agent read-only, then earn each additional capability one verb at a
    time, each with its own RBAC rule and review") — Halo operationalizes the
    same graduated-capability principle with a different mechanism: reads flow
    freely through the existing RBAC, every mutating tool earns a per-action
    human approval rather than a pre-granted verb.

- **Contradicts**: None. No contradiction issue filed. The one candidate
  tension — `docs-langfuse-mcp-server.md` **Claim 9** ("Both read and write
  tools are available by default. If you only want to use read-only tools,
  configure your MCP client with an allowlist to restrict access to write
  operations.") versus Halo's pause-before-mutation gate — is a difference of
  *surface*, not of claim: that claim describes the raw MCP endpoint's
  defaults for arbitrary external clients, while Halo is the vendor's own
  first-party wrapper which imposes an additional approval layer on top of
  the same tools. Both statements are true simultaneously; per MINER.md §4a
  this is a conditioning variable, not a contradiction. Likewise the
  2026-06-19 changelog's "Halo is Langfuse Cloud only" versus today's
  self-hosted public beta is release-time evolution, not opposing claims.

- **Extends**:
  - `docs-langfuse-mcp-server.md` (#131) — Halo is the first *in-product*
    consumer of the authenticated data-platform MCP server that note
    documents (its Claim 8, project-scoped Basic-Auth stateless server).
    Where that note flags write-tools-on-by-default as a blast-radius default
    (Claim 9), Halo shows the vendor's own answer for its UI: an approval
    gate plus session permission-scoping (Claim 2 here). Also inherits that
    note's `LANGFUSE_MCP_ALLOWED_HOSTS` / Host-header 403 operational detail,
    now with the concrete consumer (Halo's worker→web MCP hop).
  - `docs-langfuse-roadmap.md` (#320) **Claim 4** ("Build the first
    in-product Langfuse agent for reading Langfuse data, using screen
    context, and helping with tasks such as comparing traces.") — Halo *is*
    that roadmap item shipped: screen context = the UI-context injection in
    Claim 1 here. The roadmap planned it; this page documents the shipped
    mechanics, including the approval model the roadmap never mentioned.
  - `docs-langfuse-agent-skill.md` (#1056) **Claim 10** (SKILL.md
    `allowed-tools` frontmatter scoping the skill's shell blast radius at
    packaging time) — Halo is the runtime analogue for an in-product agent:
    authorization enforced per action at execution time (approval gate +
    session permissions) rather than declared once at packaging time. The two
    notes together bracket the scoping spectrum: static allowlist vs dynamic
    human-in-the-loop approval.
  - `docs-langfuse-security-and-guardrails.md` (#321) **Claim 1** (two-pronged
    security: runtime blocking guardrails + post-hoc observability) — Halo
    adds a third, interaction-level layer that note does not cover: human
    authorization of agent mutations, scoped to existing RBAC. Complementary
    Ch06 material, not overlapping claims.

- **Novel** (first appearances in the corpus):
  - The **permission-preserving approval gate** — "Approval does not grant
    additional access," approvals scoped to the signed-in user's existing
    project permissions, and conversation-scoped "Always approve" (Claim 2).
    No prior note documents an approval model that is explicitly
    non-escalating.
  - **UI-context injection** into an agent prompt (current trace/observation/
    session/dashboard plus user name, browser language, timezone) as a
    documented feature (Claim 1) — previously only a roadmap intention.
  - The **sandbox-as-infrastructure detail for agent code execution**: Lambda
    MicroVM with deny-all security group, the `INTERNET_EGRESS` default-route
    footgun, build-vs-execution role separation, and the "no Langfuse
    DB/storage/secrets on the execution role" rule (Claim 7). The corpus has
    sandbox *prescriptions*; this is a concrete sandbox *deployment contract*.
  - The **self-hosted prerequisite chain and queue-capacity split** —
    instance-wide model on web+worker, `LANGFUSE_IN_APP_AGENT_ENABLED` making
    workers consume the run queue (Claim 4) — the operational cost of running
    an in-product assistant yourself.
  - **Tracing the assistant in a dedicated project** with the explicit
    cross-project data-read exposure warning (Claim 8) — agent-run telemetry
    as an aggregate-sensitive dataset needing its own access boundary.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add Halo as the concrete
  vendor-shipped worked example of the "agent with approval gates over
  production observability data" pattern — evidence: Claim 2 (pause before
  mutating; approval non-escalating; per-conversation "Always approve"),
  Claim 6 (durable background runs, per-user/per-project conversations), and
  the example prompts table (investigate latency, cluster failed observations
  over 7 days, build dashboards) as templates for read-side delegation.
  Pair with `docs-google-sre-prodcast-04-09-ai-agents.md` Claim 3 so the
  chapter shows principle (deny writes, human permission) and implementation
  (Halo's gate) side by side. Also record the model-coupling caveat (Claim 10)
  — a gated tool loop validated against one model is a portability risk when
  choosing the model for an approval-gated agent.
- **Chapter 06 (Security and Trust)**: Highest-value target. Specific
  additions: (i) the approval-grants-no-extra-access scoping line (Claim 2)
  as the model for non-escalating human authorization; (ii) the sandbox
  egress footgun (Claim 7) — deny-all SG defeated by AWS's default
  `INTERNET_EGRESS` unless an egress connector is attached — plus the
  execution-role no-data-access rule, as a worked least-privilege example for
  running agent-written code; (iii) the dedicated-trace-project warning
  (Claim 8): assistant traces aggregate reads from other projects, so their
  sink needs its own access boundary; (iv) org-level opt-in and the separate
  AI-feature-tracing toggle (Claim 11) as the governance split between using
  AI features and letting their traffic be recorded for improvement.
  Contrast with the raw-MCP write-by-default posture in
  `docs-langfuse-mcp-server.md` Claim 9 to show where the enforcement layer
  sits (endpoint defaults vs wrapper policy).
- **Chapter 02 (Observability)**: Note briefly that observability vendors now
  ship first-party assistants *over* the telemetry with the same tool surface
  external agents get (Claim 1), and that operators can opt into tracing the
  assistant itself via `LANGFUSE_AI_FEATURES_PROJECT_ID` (Claim 8) — agent
  runs over your data are themselves observable, and unset-by-default keeps
  privacy the baseline.
- **Not recommended**: Do not cite this page as evidence that approval gates
  *work* in practice — there are zero metrics, incident reports, or
  practitioner accounts; all effectiveness/security language is vendor design
  intent (per the Prospector: "grade effectiveness/security claims as vendor
  assertion"). Also do not carry the changelog's "Cloud only" forward —
  self-hosted public beta supersedes it. Skip the plan-availability table and
  feedback sections per triage.

## Extraction Notes

- Source fetched 2026-10-17 via WebFetch (Langfuse serves docs as plain
  Markdown by appending `.md`; the same works for all followed sub-pages).
  Quotes were copied character-for-character from the fetched Markdown with
  only inline-link markup, `**bold**` markers, and inline-code backticks
  rendered away — no splicing
  of non-adjacent sentences; where a quote spans a list item it is a single
  contiguous fragment.
- miner-related-notes.md candidates processed (cite or dismiss each):
  - `docs-langfuse-security-and-guardrails.md` — **Cited** (Extends —
    adjacent Ch06 guardrail architecture; complementary layer, no claim
    overlap).
  - `docs-langfuse-mcp-server.md` — **Cited** (Extends — the MCP tool surface
    Halo wraps; write-by-default tension explicitly assessed as not a
    contradiction).
  - `docs-langfuse-agent-skill.md` — **Cited** (Extends — packaging-time
    `allowed-tools` scoping vs Halo's runtime approval gate).
  - `docs-langfuse-roadmap.md` — **Cited** (Extends/Corroborates — its Claim 4
    in-product-agent-with-screen-context item is Halo shipped).
  - `docs-langfuse-sdk-overview.md` — **Dismissed**. SDK instrumentation
    methods and OTel span mapping; no agent-action-authorization content.
  - `docs-litellm-batches-api.md` — **Dismissed**. Batch rate-limit token
    accounting; lexical noise, no topical overlap with Halo.
  - `docs-litellm-cost-map-and-response-cost.md` — **Dismissed**.
    `response_cost` accessors and pricing-dict ownership; unrelated.
  - `docs-litellm-bedrock-invoke.md` — **Dismissed**. Bedrock native Invoke
    passthrough routing; "Bedrock" appears in Halo only as Cloud hosting
    (Claim 5), not as an API surface — different layer entirely.
  - `docs-google-sre-eliminating-toil.md` — **Dismissed**. Toil taxonomy and
    measurement; background runs (Claim 6) are not toil-reduction evidence and
    the note makes no such claim.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — **Cited** (Corroborates —
    Claim 3 default-deny-writes + human permission + sandbox).
- Additional manual search of `source-notes/`: `docs-langfuse-glossary.md`
  Claim 12 (Cited — same feature, earlier name) and
  `blog-cncf-cluster-aware-ai-agent-argo-gitops.md` Claim 3 (Cited —
  graduated capability). `docs-langfuse-alerts.md` and
  `docs-langfuse-metrics-overview.md` — **Dismissed**: they document the data
  Halo queries (per the Prospector), not Halo's own claims. All three cited
  claims were re-read in their host notes and quoted verbatim (MINER.md §4b).
- `confidence_overall: emerging` — the page documents a public-beta feature;
  mechanics/prerequisites/env-vars are settled facts of the docs as fetched,
  but approval-model effectiveness, sandbox-isolation strength, and Cloud
  data-handling guarantees are vendor assertion with no practitioner or
  adversarial validation, and the self-hosted config is explicitly
  not-SemVer-covered. Claim-level grading reflects the split (settled for
  config/architecture facts, emerging for design-intent/security claims).
- No contradiction with an existing note surfaced (see Cross-References →
  Contradicts), so no contradiction issue was filed. No part of the source was
  paywalled or unreadable.
