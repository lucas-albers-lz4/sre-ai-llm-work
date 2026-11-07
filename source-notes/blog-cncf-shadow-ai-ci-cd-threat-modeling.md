---
source_url: https://www.cncf.io/blog/2026/08/07/shadow-ai-in-ci-cd-threat-modeling-the-path-from-developer-laptop-to-kubernetes
source_type: blog-post
title: "Shadow AI in CI/CD: Threat-modeling the path from developer laptop to Kubernetes"
author: "Matteo Bisi (ReeVo SpA)"
date_published: 2026-08-07
date_extracted: 2026-11-07
last_checked: 2026-11-07
status: current
confidence_overall: emerging
issue: "#1982"
---

# Shadow AI in CI/CD: Threat-modeling the path from developer laptop to Kubernetes

> A reference threat model that reframes Shadow AI as an access / non-human-identity
> problem, then supplies the reusable governance structures the corpus lacks: a
> six-stage delivery-path risk taxonomy, an AI-inventory schema, a
> capability-to-control blast-radius matrix, a restart-only RBAC worked example,
> and a dated 2026 snapshot of the agent-governance tooling gap.

## Source Context

- **Type**: blog-post (CNCF Member Post, published 2026-08-07).
- **Author credibility**: Matteo Bisi, ReeVo SpA (a consultancy). The post is a
  synthesis threat model and architecture-survey, not a first-person operational
  account: it reports no production deployment, no incident, no metrics, and no
  configuration lifted from a running environment. Its checkable content is the
  control structure and the dated tooling/maturity claims. Licensing remarks are
  asserted, not verified against upstream repos.
- **Scope**: Covers a cloud-native delivery path from developer laptop → source
  control → CI → artifact registry → CD → Kubernetes runtime; per-stage Shadow AI
  risk and controls; an AI inventory; treating agents as identities; a
  blast-radius control matrix; defense in depth; and a 2026 CNCF/OOS tooling map
  with maturity and license caveats. It does NOT cover implementation manifests,
  measured attack outcomes, incident data, model-evaluation methodology, or the
  mechanics of delegation/principal identity (a separate concern covered by other
  notes in the corpus).
- **Prospector caveat applied**: treat as reference architecture / threat model,
  confidence `emerging`. Do not re-extract generic supply-chain signing/SBOM/
  admission-control advice as new; extract the governance layer, the stage axis,
  and the blast-radius material.

## Extracted Claims

### Claim 1: Shadow AI is an access problem, not merely a chatbot-policy problem — an ungoverned agent becomes a new non-human identity with permissions, a blast radius, and a place in the threat model
- **Evidence**: The article's definition of Shadow AI and its explicit reframing;
  no incident data or measured exposure backs it.
- **Confidence**: emerging (a well-argued framing position from a consultancy
  survey, not an implementation report).
- **Quote**: "For platform and security teams, Shadow AI is not really a “developers using a chatbot” problem. It is an access problem."
- **Quote**: "And once an AI system is allowed to *call tools* and *take actions*, it stops being productivity software and becomes a new non-human identity with permissions, a blast radius, and a place in your threat model."
- **Our assessment**: Buy the framing. It is the same distinction the corpus's
  agent-auth material draws structurally — an agent is not the user and carries
  its own identity (`blog-cncf-agent-auth-lawyers-day-in-court`, Claim 12) — but
  this source states the *governance* consequence: once an agent has credentials
  it must be inventoried, owned, scoped, monitored, and revocable. The article is
  advisory; the corpus's practitioner notes (`blog-cncf-cloud-native-agentic-ai-security-platform`,
  Claim 2) supply the working identity mechanism this framing assumes.

### Claim 2: Risk rises sharply when AI moves from giving advice to taking action — an agent with a Git token, cloud credentials, or a Kubernetes ServiceAccount can mutate resources at machine speed, and Kubernetes does not distinguish a harmful action by an attacker from the same action by an over-privileged automation identity
- **Evidence**: Argument by contrast between an assistant that suggests code and an
  agent that acts; the Kubernetes indistinguishability point is a statement about
  API-server authorization, not a measured incident.
- **Confidence**: emerging (sound architectural reasoning; unvalidated in the
  source).
- **Quote**: "The risk rises sharply when AI stops **giving advice** and starts **taking action**."
- **Quote**: "An agent with a Git token, cloud credentials, or a Kubernetes ServiceAccount creates a different class entirely. It can create, alter, or delete resources at machine speed, and Kubernetes will not distinguish between a harmful action taken by an attacker and the same action taken by an over-privileged automation identity."
- **Our assessment**: Buy the action/advice axis — it is Ch06's existing
  "Shadow → suggest → act" ladder stated as a threat-model boundary. The
  Kubernetes sentence is accurate for *identity authorization*: the API server
  authorizes by RBAC and has no notion of intent. It does not contradict the
  corpus's agent-identity work, which adds a distinguishable agent identity
  *above* the Kubernetes ServiceAccount; it says that identity alone does not
  encode whether the action is safe. That is the argument for Claim 7's
  capability-to-control mapping.

### Claim 3: Shadow AI can be injected at six distinct delivery stages — developer laptop, source control, CI pipeline, artifact registry, CD platform, Kubernetes runtime — each with a typical use and a stage-specific primary risk, and a convenience decision early in the path becomes a production exposure at the end
- **Evidence**: A six-row stage/use/risk table (reproduced in Concrete Artifacts).
  No incident examples or measurements accompany the rows.
- **Confidence**: emerging (a usable taxonomy; the per-stage risk attribution is
  the author's analysis rather than observed events).
- **Quote**: "Shadow AI can appear at every stage, and a small convenience decision at the start of the path can become a production exposure at the end."
- **Our assessment**: This is the article's most reusable structural artifact. The
  guide already has a *trust* axis (shadow → suggest → act) but no *stage* axis;
  this table supplies one. Note the risk character changes along the path: the
  early stages are dominated by **data egress** (source, secrets, architecture
  leaving approved boundaries), while the late stages are dominated by
  **privileged action** (bypassed change controls, destructive ServiceAccounts).
  That split is what makes a single "AI security" control insufficient and is
  worth preserving when this is folded into Ch06.

### Claim 4: Prompt injection is the through-line risk because agents routinely read untrusted content — issue descriptions, READMEs, dependency changelogs, build logs — so prompt filtering alone is never enough and defense in depth is the real answer
- **Evidence**: Named untrusted-content sources plus the OWASP AI/LLM guidance as
  a baseline; no red-team results or bypass examples.
- **Confidence**: emerging (consistent with the corpus and OWASP; asserted rather
  than demonstrated here).
- **Quote**: "Prompt injection is the through-line. Agents routinely read untrusted content: issue descriptions, READMEs, dependency changelogs, build logs. Any of it can steer an agent into disclosing data or taking an unsafe action, which is why prompt filtering alone will never be enough and defense-in-depth is the real answer."
- **Our assessment**: Buy it, and note it is the premise for the rest of the
  article's controls: if the model can be steered, the enforceable boundaries must
  sit outside the model (network, identity, admission, RBAC). It independently
  matches `blog-cncf-network-boundary-ai-agents-nginx-otel`, Claim 4 ("Restricting
  where an agent can communicate does not guarantee that its decisions are correct
  or safe") — that note supplies the boundary half, this one supplies the
  "assume the model is steered" posture.

### Claim 5: An AI inventory is the precondition for every other control — each entry records business and technical owner, purpose/users, permitted data classification, connected systems and permissions, model/provider, production status, last review, and revocation path
- **Evidence**: The article's explicit field list and its assertion that "every
  other control on this list assumes this one exists." No sample inventory or
  registry artifact is shown.
- **Confidence**: emerging (a checklist from a survey; not validated against an
  operating inventory).
- **Quote**: "Keep a living inventory of approved and discovered AI tools, models, extensions, code assistants, agents, API integrations, and MCP servers. Each entry needs a business and a technical owner, its purpose and users, the data classification it is allowed to touch, the systems it connects to and with what permissions, the model or provider behind it, whether it is in production, when it was last reviewed, and how to revoke its access. You cannot govern what you cannot see, and every other control on this list assumes this one exists."
- **Our assessment**: Buy the schema. It extends the guide's existing rule to
  "maintain an auditable inventory of every component in the deployed AI stack"
  (`guide/06-security-and-trust.md:537`) from component enumeration to
  *ownership + permission + revocation* — the fields that make an inventory
  actionable during an incident. The article also names two implementation
  options worth recording: model agents and MCP servers as **Backstage catalog
  components** (reusing existing ownership tooling) or **agentregistry** (early
  stage — see Claim 11). The checklist is a minimum schema, not evidence that any
  organization maintains one.

### Claim 6: Every agent should have a unique identity and must never borrow a developer's personal credentials or a shared admin account; least-privilege defaults are separate credentials per environment, short-lived tokens, read-only where possible, namespace-scoped Kubernetes permissions, explicit allowlists, and immediate revocation
- **Evidence**: An explicit rule plus a six-item least-privilege list. No
  implementation or credential-issuance detail is shown beyond naming
  SPIFFE/SPIRE, cert-manager, and Keycloak as anchors.
- **Confidence**: emerging (a policy checklist; the mechanisms are standard and
  covered with more depth elsewhere in the corpus).
- **Quote**: "Every agent should have a unique identity. It should never borrow a developer’s personal credentials or a shared admin account. Least privilege by default means:"
- **Our assessment**: Buy the rule — "never borrow a developer's personal
  credentials" is the sharpest short form of the non-human-identity requirement,
  and it corroborates `docs-google-sre-ai-engineering-reliable-operations`,
  Claim 4 ("Agent identities must be distinct from human users, strongly
  authenticated, and granted access only on-demand") and the identity/delegation
  decomposition in `blog-cncf-agent-auth-lawyers-day-in-court`, Claim 5 and
  Claim 12. Scope limit: this article stops at *agent* identity and does not
  address the separate *principal* identity (the user on whose behalf the agent
  acts), which the agent-auth note covers. For the guide, keep the two layers
  distinct rather than treating "unique agent identity" as the whole story.

### Claim 7: Match the control to the blast radius — a capability ladder from code explanation through autonomous production changes maps each AI capability to an escalating required control level
- **Evidence**: A six-row capability/control table (reproduced in Concrete
  Artifacts). The ladder is prescriptive; no calibration data or failure cases
  justify the specific boundaries.
- **Confidence**: emerging (a usable decision selector, not a validated model).
- **Quote**: "Not every AI function needs the same treatment:"
- **Our assessment**: Buy it as a *selector*, not as settled policy. It gives Ch06
  something the trust ladder does not: a way to assign a control level from the
  capability being granted, rather than from a global posture. The escalation is
  coherent — approved tool → human review → restricted repo permissions →
  isolated execution + policy-as-code + approval gate → namespace RBAC + audit +
  human approval → exceptional approval + time-bound access + kill switch. Pair
  it with `blog-cncf-cloud-native-agentic-ai-security-platform`, Claim 9, which
  implements the top of the ladder as an escalation trigger when a proposed action
  would exceed a configured blast radius. The article gives no evidence that these
  particular control levels are sufficient; grade the table as design guidance.

### Claim 8: A restart-only remediation agent needs a namespaced Role on `apps`/`deployments` granting only `get`, `list`, and `patch` — because a rollout restart is a patch, `create` and `delete` are never needed
- **Evidence**: A worked RBAC derivation in prose; no manifest is shown. The
  underlying Kubernetes facts (rollout restart mutates the pod template via a
  patch; RBAC verbs and namespace scope) are standard API semantics.
- **Confidence**: emerging (the article's example is prescriptive and unmanifested;
  the RBAC/rollout mechanism itself is a Kubernetes guarantee).
- **Quote**: "For example, an agent whose only job is to restart a Deployment needs a namespaced Role, not a cluster-wide one: bound to a single namespace, limited to the apps API group and the deployments resource, and granting only get, list, and patch (a rollout restart is a patch, so create and delete are never needed). That is a world away from cluster-admin: even if the agent is fully under someone else’s control, it cannot read secrets, touch other namespaces, or delete workloads."
- **Our assessment**: Buy the derivation. It is the corpus's clearest worked
  example of *deriving* the verb set from the task rather than starting from a
  broad role, and it is a direct instance of
  `blog-cncf-cluster-aware-ai-agent-argo-gitops`, Claim 3 ("start every agent
  read-only, then earn each additional capability one verb at a time, each with
  its own RBAC rule and review"). The important transferable move is that the
  agent's *only* mutation need (`patch`) is visible in the role; `create` and
  `delete` are absent because the task never requires them. The safe claim is
  scoped to this task; a different remediation task needs its own derivation.

### Claim 9: In Kubernetes-native CI, an admission policy is a hard gate an agent cannot talk its way past — a Kyverno or OPA/Gatekeeper rule rejecting unsigned images holds regardless of what a compromised pipeline job tries to push
- **Evidence**: The enforcement argument (policy is evaluated by the cluster, not
  the agent) plus named tools; no bypass analysis.
- **Confidence**: emerging (the enforcement-below-the-model property is real; the
  "hard gate" is conditional on correct, reachable admission — see assessment).
- **Quote**: "In Kubernetes-native CI, an admission policy is a hard gate that an agent cannot talk its way past: a Kyverno or OPA/Gatekeeper rule that rejects unsigned images, for instance, holds regardless of what a compromised pipeline job tries to push."
- **Our assessment**: Buy the placement argument — an admission decision is made
  outside the model's trust domain, so prompt injection cannot negotiate with it.
  But the article's "hard gate" is stronger than the corpus's evidence supports:
  `blog-cncf-runtime-supply-chain-verification-nri`, Claim 1 documents that
  admission webhooks are necessary but insufficient — misconfigured selectors,
  webhook outages, static pods, and direct kubelet access can skip verification
  entirely. The guide should state the article's rule with that qualification:
  *when correctly configured and reachable*, admission is the hard gate; it is not
  unconditional. This is a qualification, not a contradiction.

### Claim 10: In a GitOps delivery model the pull request is the approval gate — the agent proposes a manifest change, a human approves the merge, and Argo CD or Flux reconciles only what is already merged; no path to production should skip the gate
- **Evidence**: The architectural argument, with named controllers and the
  claim that neither controller takes instructions from the agent. No incident or
  configuration example.
- **Confidence**: emerging (a sound control pattern; the security property depends
  on the agent's write access to Git and the controller).
- **Quote**: "In a GitOps model, the pull request *is* the approval gate: the agent proposes a manifest change, a human approves the merge, and the GitOps controller (**Argo CD** or **Flux**) reconciles. Neither controller takes instructions from the agent; it only ever applies what is already merged. Enforce that no path to production exists that skips the gate."
- **Our assessment**: Buy the pattern and the "no path around the gate" rule. It
  complements `blog-cncf-cluster-aware-ai-agent-argo-gitops`, Claim 4: that note
  records GitOps as an *audit* artifact for agent configuration; this source makes
  the PR an *approval* boundary for production change. The conditional the article
  leaves implicit: "neither controller takes instructions from the agent" holds
  only if the agent cannot write to the deployment repo or the controller's
  config. An agent with commit access to the GitOps repo is *inside* the gate, and
  the whole property collapses. The guide should state that precondition.

### Claim 11: The 2026 agent-governance tooling layer is immature — no graduated project owns prompt inspection, agent discovery, and tool-call policy end to end — while the pipeline and runtime layers are well served; the named candidates are kagent (CNCF Sandbox, May 2025), Envoy AI Gateway v1.0 (June 2026), agentgateway (Linux Foundation), and agentregistry (submitted to CNCF Sandbox March 2026, still under review)
- **Evidence**: A dated landscape table plus a project-by-project narrative. The
  maturity/date claims are checkable snapshots; the article does not benchmark the
  projects.
- **Confidence**: emerging (a dated survey, not an evaluation; several projects
  are explicitly early-stage).
- **Quote**: "The gaps deserve the same bluntness. The pipeline and runtime layers are well served by mature CNCF projects. AI governance itself is thinner: prompt inspection, agent discovery, tool-call policy. No project at graduated maturity owns that space end to end, and the ones aimed squarely at it are young, though the gateway layer improved noticeably during 2026."
- **Quote**: "**kagent** (CNCF Sandbox, accepted May 2025) is a framework for building and running agents in Kubernetes, which at least puts agent workloads under the same declarative model as everything else in the cluster."
- **Quote**: "**Envoy AI Gateway** (Apache-2.0) reached v1.0 in June 2026, with contributions from Bloomberg, Nutanix, Tetrate, and the Envoy community. It uses a two-tier pattern: an outer gateway for authentication and global rate limiting, an inner one for fine-grained control over self-hosted model endpoints, plus routing for MCP traffic."
- **Quote**: "**agentregistry** targets the inventory problem directly, cataloging MCP servers, agents, and skills and scanning connected runtimes to surface what was never registered. It was submitted to the CNCF Sandbox in March 2026, but the application is still under review, so evaluate it as an early-stage project rather than a CNCF-governed one."
- **Our assessment**: Buy this as a *dated snapshot*, not as settled fact. Ch06
  currently discusses agent gateways generically ("An agent gateway's default is
  full access") without naming the project layer or its maturity; this source
  gives the missing names and the honest caveat. The "no graduated project owns
  agent governance end to end" sentence is the important guide-level claim: it
  means a team adopting this stack is assembling a control plane from young
  parts, not buying a finished one. Record the dates with the claims so a later
  Smith can age the snapshot rather than treat it as permanent.

### Claim 12: Open source is not the same as foundation-governed, and licenses carry obligations — several entries are single-vendor open-core projects, and TruffleHog, Zitadel, and Teleport's community edition are AGPL-3.0 with network-service source-disclosure obligations
- **Evidence**: A named list of single-vendor projects and a license table. The
  licensing statements are asserted in the article and were not independently
  verified during this extraction.
- **Confidence**: emerging (a procurement caution; license facts need checking
  against upstream repos before reuse).
- **Quote**: "First, open source is not the same as foundation-governed. Several of those entries are single-vendor projects with an open source core and a paid edition: Calico by Tigera, Tracee by Aqua, TruffleHog by Truffle Security, ToolHive by Stacklok, Teleport by Gravitational. They are legitimate choices, but check that the capability you are actually relying on is in the free edition."
- **Quote**: "Second, read the license before you embed or redistribute. gitleaks is MIT; Tracee, Polaris, Calico, and ToolHive are Apache-2.0. TruffleHog, Zitadel, and Teleport’s community edition are AGPL-3.0, which carries source-disclosure obligations if you offer a modified version as a network service."
- **Our assessment**: Buy the *caution*, not the specific license table. The
  guide's tool recommendations should not inherit a vendor-OSS name as if it were
  neutral, and "verify the capability is in the free edition" is a real
  procurement trap. Because this extraction did not verify any license against an
  upstream repository, the table should be treated as a prompt to check, not as a
  citation-grade license record.

### Claim 13: Scanning MCP servers for tool poisoning and prompt-injection payloads has no foundation-governed answer — the maintained options are vendor-developed, so it is an evaluation exercise; the pragmatic stance is a policy enforcement point in front of model/tool endpoints plus identity and admission controls that constrain what an agent can do even when its reasoning cannot be fully inspected
- **Evidence**: An explicit gap statement plus the recommended fallback posture;
  no scanner comparison or detection-rate data.
- **Confidence**: emerging (a landscape observation with a reasoned fallback; no
  measurement).
- **Quote**: "One layer still has no foundation-governed answer: scanning MCP servers for tool poisoning and prompt-injection payloads. Tooling exists, but the maintained options are vendor-developed, so treat that as an evaluation exercise rather than a settled choice. Until it matures, the pragmatic position is unchanged. Pair OWASP guidance with a policy enforcement point in front of model and tool endpoints, then lean on the identity and admission controls above to constrain what an agent can *do*, even when you cannot fully inspect what it is *thinking*."
- **Our assessment**: Buy it. This is the article's most honest statement and it
  matches the corpus's boundary evidence: network placement cannot validate
  intent (`blog-cncf-network-boundary-ai-agents-nginx-otel`, Claim 4), and
  safety constraints should be deterministic policy outside the model
  (`blog-cncf-cloud-native-agentic-ai-security-platform`, Claim 3). The guide
  should record the gap as a gap, not paper over it with a tool recommendation:
  MCP tool-poisoning inspection is not a solved layer in 2026, so the enforceable
  controls remain identity, admission, network, and RBAC.

### Claim 14: An autonomous agent that runs commands should run in a disposable, VM-isolated workspace with its own kernel and filesystem, where the host's SSH keys, cloud credential files, and repository checkouts are absent — if it is manipulated, the environment is discarded
- **Evidence**: The isolation mechanism and the property it provides (absent
  credentials, disposable damage boundary); implementations are named only
  generically, with open-source examples deferred to the tooling table.
- **Confidence**: emerging (a sound isolation property; no benchmark or escape
  analysis in the source).
- **Quote**: "The mechanism worth understanding is a disposable, VM-isolated workspace: the agent gets its own kernel and filesystem, and the host’s SSH keys, cloud credential files, and other repository checkouts are simply not present inside it. If the agent is manipulated into doing something destructive, you throw the environment away and the damage stops there."
- **Our assessment**: Buy the property-over-product framing. It is the same
  division of labor the corpus records for agent-sandbox: Kubernetes handles
  placement, gVisor/Kata handle containment
  (`blog-linsun-sandboxing-agent-not-enough`, Claim 2), and sandboxing is
  necessary but not sufficient (that note's Claim 3). This article adds the
  *credential-absence* argument explicitly: the point is not just that the agent
  cannot escape, but that the secrets are not inside the environment to steal.

## Concrete Artifacts

### Six-stage delivery path (verbatim from the article)

```
Delivery stage          Typical Shadow AI use                                   Primary risk
Developer laptop        Unapproved code assistant, local model plugin, public   Source code, secrets, or architecture leave approved
                        chatbot                                                 boundaries
Source control          AI bot reviews PRs, generates commits, summarizes      Excessive repo permissions, unsafe code changes, no clear
                        repositories                                            ownership
CI pipeline             AI generates pipeline logic, analyzes logs, “fixes”     Build secrets and cloud credentials exposed; automated
                        failing builds                                          supply-chain changes
Artifact registry       AI-assisted image or dependency selection               Vulnerable, malicious, or untraceable dependencies reach
                                                                                production
CD platform             AI agent approves, modifies, or rolls out releases      Bypassed change controls, unauthorized deployment, poor
                                                                                traceability
Kubernetes runtime      Agent queries clusters, remediates alerts, scales       Over-privileged ServiceAccounts, destructive actions,
                        workloads                                               lateral movement
```

Attribution: "The delivery path" section of the article. The column layout was
reflowed for the note; the cell text is unchanged.

### Capability-to-control blast-radius matrix (verbatim from the article)

```
AI capability                              Recommended control level
Code explanation or documentation drafting Approved tool, data-classification rules, developer training
Code suggestion                            Human review, standard testing, secret scanning, dependency checks
Pull-request creation                      Restricted repo permissions, mandatory peer review
CI/CD pipeline modification                Isolated execution, policy-as-code checks, approval gate
Cluster remediation                        Strict namespace RBAC, limited scope, full audit trail, human
                                           approval for high-impact actions
Autonomous production changes              Exceptional approval only, time-bound access, kill switch,
                                           continuous monitoring
```

Attribution: "Match the control to the blast radius" section.

### AI inventory fields and agent least-privilege defaults (verbatim from the article)

```
Each entry needs a business and a technical owner, its purpose and users, the
data classification it is allowed to touch, the systems it connects to and with
what permissions, the model or provider behind it, whether it is in production,
when it was last reviewed, and how to revoke its access.
```

```
Least privilege by default means:
- Separate credentials per environment
- Short-lived tokens, not persistent secrets
- Read-only access where possible
- Namespace-scoped Kubernetes permissions
- Explicit allowlists for APIs, tools, repositories, and MCP servers
- Immediate revocation
```

Attribution: "Build an AI inventory" and "Treat AI agents as identities" sections.

### Agent-governance tooling row (verbatim from the article's tooling table)

```
Area                          CNCF projects                                      Other open source                                What it addresses
Agent governance: discovery,  kagent (sandbox), Envoy AI Gateway (extension of    agentgateway, agentregistry, ToolHive,           Register and discover agents and MCP servers,
tool-call policy              Envoy Gateway; Envoy graduated), Backstage         ContextForge MCP Gateway                         authenticate and authorize tool calls, trace
                              (incubating), OpenTelemetry (graduated)                                                              what an agent actually invoked
```

Attribution: "Tooling by area (CNCF and open source)" section. Layout reflowed;
cell text unchanged.

## Cross-References

**Candidates from `miner-related-notes.md` (all ten listed paths evaluated; one
cited, nine dismissed):**

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SLO granularity and migration practice; no agent security,
  identity, or delivery-path content.
- `source-notes/blog-cncf-cloud-native-agentic-ai-security-platform.md` —
  **cited** (Corroborates / Extends): the closest corpus note and the
  practitioner counterpart. Its **Claim 3** (safety constraints belong in
  policy-as-code, not in the reviewer's system prompt) is the implementation
  of this source's placement argument (Claims 4, 9, 13); its **Claim 9** puts
  blast radius on the escalation path ("the proposed action would exceed a
  configured blast radius"), which is the runtime form of this source's Claim 7
  capability ladder; its **Claim 2** (cert-manager per-agent identities +
  CiliumNetworkPolicy) is the working identity mechanism behind Claim 6. This
  source is advisory and broader; that note holds the evidence-bearing depth.
- `source-notes/docs-promptfoo-model-audit.md` — **dismissed**: local model
  artifact scanning and scanner CLI flags; the shared "security scanning" theme
  is too loose to be an evidential cross-ref.
- `source-notes/blog-cncf-inspektor-gadget-security-audit.md` — **dismissed**:
  eBPF toolkit's own security audit; not about governing AI use in a delivery
  path.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **dismissed**: config-language semantics and declarative change workflows; the
  article's GitOps material (Claim 10) is about the approval gate, not config
  evaluation.
- `source-notes/docs-google-sre-prodcast-03-01.md` — **dismissed**: SRE
  methodology, org dynamics, and observability adoption; no agent-security
  content.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**:
  within-request model composition; unrelated.
- `source-notes/docs-litellm-completion-function-call.md` — **dismissed**:
  capability predicates and tool-call support; narrower than this source's
  governance layer and not about authorization policy.
- `source-notes/docs-litellm-creating-adapters.md` — **dismissed**: custom
  format translation; unrelated.
- `source-notes/docs-litellm-mcp-oauth.md` — **dismissed**: MCP OAuth flow
  mechanics; this source's gap statement (Claim 13) is about tool-poisoning
  inspection, not OAuth authentication.

**Additional cross-references found by searching `source-notes/`:**

- **Corroborates**:
  - `blog-cncf-agent-auth-lawyers-day-in-court` **Claim 5** ("Before the system
    can trust an agent, it needs to know exactly which agent is making the
    request") and **Claim 12** ("An agent is not the user") — this source's
    "never borrow a developer's personal credentials" rule (Claim 6) is the
    governance-side statement of the same identity separation. Together they say
    an agent needs *its own* identity and a separate *principal* identity; this
    note supplies only the first.
  - `docs-cncf-iam-whitepaper-reference-patterns` **Claim 2** (identity
    explicitly includes automated agents as first-class subjects of
    authentication and authorization decisions) — the IAM standard's vocabulary
    for this source's Claim 6.
  - `docs-google-sre-ai-engineering-reliable-operations` **Claim 4** ("No
    ambient access & least privilege — agent identities must be distinct from
    humans, strongly authenticated, on-demand, with circuit breakers and
    mandatory dry-run support for every API") and
    **Claim 2** (Progressive Authorization) — Google's production form of this
    source's identity checklist and capability ladder. **Claim 5** (Actus as a
    decoupled safety gateway) is the stronger architectural version of the
    article's "policy enforcement point" fallback (Claim 13).
  - `blog-cncf-cluster-aware-ai-agent-argo-gitops` **Claim 2** (read-only RBAC
    as the load-bearing safety decision) and **Claim 3** ("start every agent
    read-only, then earn each additional capability one verb at a time") — this
    source's restart-only Role (Claim 8) is a concrete derivation of that rule.
  - `blog-cncf-securing-cicd-credentials-verification` **Claim 2** ("The
    credentials simply aren’t on the runner") — the first-party CI/CD
    credential-isolation account; this article generalizes the same
    absent-credential principle to Shadow AI agents across all six stages.
  - `blog-cncf-network-boundary-ai-agents-nginx-otel` **Claim 1** (the boundary
    must be architectural, enforced regardless of application policy) and
    **Claim 4** (network control does not establish intent) — the network half
    of this source's defense-in-depth posture (Claims 4, 9, 13).
  - `blog-linsun-sandboxing-agent-not-enough` **Claim 3** ("Sandboxing your
    agents is necessary, but not sufficient") — this source's disposable
    VM-isolated workspace (Claim 14) is one layer; the sandbox note supplies the
    efficiency caveat this article does not address.
- **Extends**:
  - `blog-cncf-cloud-native-agentic-ai-security-platform` **Claim 3** — this
    source extends the policy-as-code placement rule from the reviewer-agent
    decision path to the whole delivery pipeline (CI admission, CD approval
    gate), giving the practitioner pattern a stage taxonomy.
  - `blog-cncf-runtime-supply-chain-verification-nri` **Claim 1** — qualifies
    this source's "admission policy is a hard gate" (Claim 9): admission is
    necessary but insufficient because misconfiguration, webhook outage, static
    pods, and direct kubelet access can bypass it. The guide should carry both:
    enforce below the model, but do not assume admission is unconditional.
  - `blog-cncf-policy-engine-offline-production-fidelity` **Claim 6** ("The
    point of offline testing is that it should be *identical* to what runs in
    the cluster") — the evaluation-fidelity precondition for trusting any
    admission/policy gate this source recommends; the article asserts the gate
    but does not address whether the policy itself was tested against realistic
    input.
- **Contradicts**: none filed. Two apparent tensions were examined and resolved
  as conditioning variables / qualifications under MINER.md §4a:
  1. `blog-cncf-cluster-aware-ai-agent-argo-gitops` **Claim 2** uses a
     cluster-wide read-only `ClusterRole`, while this source's Claim 8 uses a
     namespaced `Role`. The conditioning variable is the agent's legitimate
     read scope: a diagnosis agent reading pods/events cluster-wide needs the
     former; a single-namespace restart agent needs the latter. Both follow the
     same "least privilege for the task" rule, so this is not a contradiction.
  2. `blog-cncf-runtime-supply-chain-verification-nri` **Claim 1** is discussed
     above as a qualification of "hard gate", not an opposing claim.
  Checked `CONTRADICTIONS.md` and open `contradiction`-labeled issues: no
  existing entry covers Shadow AI, delivery-stage governance, or admission-gate
  sufficiency.
- **Novel** (new to the corpus):
  - **"Shadow AI" reframed as an access/non-human-identity category** (Claim 1)
    rather than an acceptable-use policy problem.
  - The **six-stage delivery-path taxonomy** (Claim 3) as a structural spine
    distinct from the guide's existing trust ladder.
  - The **AI-inventory schema** with ownership, permitted data classification,
    connected-system permissions, production status, and revocation path
    (Claim 5).
  - The **capability-to-control blast-radius matrix** (Claim 7) as a selector
    from capability to required control level.
  - The **restart-only RBAC derivation** (Claim 8) — a worked example of
    deriving verbs from the task.
  - The **2026 agent-governance tooling-gap snapshot** (Claims 11–13), including
    the explicit "no graduated project owns agent governance end to end" claim
    and the dated project maturity caveats.
  - The **open-source vs foundation-governed** procurement distinction and
    license-obligation caution (Claim 12), recorded as an asserted snapshot.

## Guide Impact

- **Chapter 06 (Security and Trust)** — `### Shadow → suggest → act, never the
  reverse` (`guide/06-security-and-trust.md:571`): add the **stage axis** (Claim
  3) alongside the trust axis, and add the **capability-to-control matrix**
  (Claim 7) as the way to select a control level once a capability is granted.
  Suggested rule: *classify an AI integration by delivery stage and by capability;
  the risk is data egress for advice-stage use and privileged action for
  action-stage use, and the required control escalates with capability, not with
  the tool's brand.* Cite this source for the taxonomy and matrix; cite
  `blog-cncf-cloud-native-agentic-ai-security-platform` Claim 9 for the runtime
  blast-radius trigger.
- **Chapter 06 (Security and Trust)** — `### Impact assessments cover the
  deployed stack, not just the model` (`guide/06-security-and-trust.md:537`):
  extend the existing inventory rule with the **ownership/permission/revocation
  fields** (Claim 5) and the **agents-as-identities checklist** (Claim 6),
  especially "never borrow a developer's personal credentials." The existing text
  says to inventory components; this source supplies the fields that make the
  inventory usable during an incident.
- **Chapter 06 (Security and Trust)** — `### An agent gateway's default is full
  access` (`guide/06-security-and-trust.md:316`): add the **2026 agent-governance
  landscape and maturity caveat** (Claim 11) — name kagent (CNCF Sandbox, May
  2025), Envoy AI Gateway v1.0 (June 2026, two-tier outer auth/rate-limit + inner
  model-endpoint control), agentgateway (LF policy proxy: JWT/API-key/OAuth, CEL
  RBAC, content filtering, OTel), and agentregistry (submitted to CNCF Sandbox
  March 2026, still under review). State the gap plainly: no graduated project
  owns prompt inspection, agent discovery, and tool-call policy end to end.
  Record the dates with the claim so the snapshot can age.
- **Chapter 06 (Security and Trust)** — the CI/CD material
  (`### Three CI/CD anti-patterns...` at `:691` and the isolation rule at
  `:725`): add the **restart-only RBAC worked example** (Claim 8), the **admission
  policy hard-gate rule** (Claim 9) with the NRI qualification, and the **GitOps
  PR-as-approval-gate rule** (Claim 10). The article gives the guide a concrete
  bridge from "isolate CI/CD stages by blast radius" to the agent-specific
  actions inside those stages.
- **Chapter 03 (Runbooks and Agents)**: add the **agent ownership/lifecycle**
  material (Claims 5–6) and the **namespace-scoped RBAC derivation** (Claim 8)
  near the existing agent-deployment guidance. The rule: a remediation agent's
  role is derived from the exact mutation it needs; a restart-only agent gets a
  namespaced `Role` on `apps`/`deployments` with `get`/`list`/`patch`, never
  cluster-admin.
- **Chapter 05 (LLM Ops Reliability)** — `### CI/CD supply-chain isolation`
  (`guide/05-llm-ops-reliability.md:1371`): this source broadens the existing
  supply-chain-focused rule to **AI-integration risk per delivery stage**
  (Claim 3) and adds the **CD/GitOps approval-gate precondition** (Claim 10).
  Keep the rule distinct from generic signing/SBOM advice, which the guide
  already covers in more depth.
- **Chapter 00 (Principles)**: record the governance principle from the
  article's close (Claims 1 and 13): *make AI use visible, accountable, and
  proportionate to its risk; the test is that if any single control fails, the
  agent must still be unable to cause material harm.* Cite this source with the
  `emerging` grade — it is a reference architecture, not a validated practice.

## Extraction Notes

- Source read in full: single CNCF blog page (member post, ~40 KB extracted
  text including site chrome; article body from the definition of Shadow AI
  through the conclusion). No sub-pages were fetched: the linked OWASP guidance
  and project repos are references, not extensions of this article's claims, and
  the article is the canonical write-up. The delivery-path diagram image was not
  OCR'd; its caption is part of the page text and is not quoted as an artifact.
- **Quote fidelity**: every `Quote` and quoted artifact passage was copied from
  the fetched page text, preserving the source's curly quotes/apostrophes
  (`“developers using a chatbot”`, `developer’s`, `someone else’s`) and its
  emphasis markers where they appear. No non-adjacent sentences were spliced;
  where a claim needed two separated source sentences, they are recorded as
  separate `Quote` lines. Tables were reflowed for readability but the cell text
  is unchanged.
- **Evidence caveats recorded per the Prospector**: the source is a synthesis
  threat model, not a first-person operational account. It contains no metrics,
  no incident narrative, no deployment scale, and no production config. License
  remarks and tooling maturity dates are asserted and dated 2026-08; they were
  not independently verified during extraction and should be treated as a
  snapshot. `confidence_overall: emerging` reflects the body of evidence; the
  restart-only RBAC mechanism is a Kubernetes guarantee but the recommendation
  itself is unmanifested.
- **`miner-related-notes.md` disposition**: all ten candidate paths evaluated —
  one cited (`blog-cncf-cloud-native-agentic-ai-security-platform`) and nine
  explicitly dismissed in Cross-References. Additional cross-refs
  (`blog-cncf-agent-auth-lawyers-day-in-court`,
  `docs-cncf-iam-whitepaper-reference-patterns`,
  `docs-google-sre-ai-engineering-reliable-operations`,
  `blog-cncf-cluster-aware-ai-agent-argo-gitops`,
  `blog-cncf-securing-cicd-credentials-verification`,
  `blog-cncf-network-boundary-ai-agents-nginx-otel`,
  `blog-linsun-sandboxing-agent-not-enough`,
  `blog-cncf-runtime-supply-chain-verification-nri`,
  `blog-cncf-policy-engine-offline-production-fidelity`) were found by searching
  `source-notes/`. Every cited `Claim N` was re-read against the named note per
  MINER.md §4b.
- **No contradiction issue filed**: the two examined tensions are a
  namespace-vs-cluster RBAC scope conditioning variable and an admission-gate
  qualification, neither of which meets the §4a bar (no opposing guide advice,
  and the guide currently states no conflicting rule). `CONTRADICTIONS.md` and
  open `contradiction`-labeled issues were checked for existing entries.
- `date_extracted` / `last_checked` set to 2026-11-07 UTC (page fetched and
  quote-verified on that date).
- No `guide/` edits, no `registry/*` edits: registry indexes are rebuilt after
  merge from this note's frontmatter and claim headings.
