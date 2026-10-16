---
source_url: https://www.cncf.io/blog/2026/06/17/why-cloud-native-belongs-at-the-heart-of-agentic-ai-lessons-from-building-a-multi-agent-security-platform-on-kubernetes
source_type: blog-post
title: "Why cloud native belongs at the heart of agentic AI: Lessons from building a multi-agent security platform on Kubernetes"
author: "Willem Berroubache (Lead Security Architect, Orange Innovation; CNCF Golden Kubestronaut)"
date_published: 2026-06-17
date_extracted: 2026-10-16
last_checked: 2026-10-16
status: current
confidence_overall: emerging
issue: "#1748"
---

# Why cloud native belongs at the heart of agentic AI: Lessons from building a multi-agent security platform on Kubernetes

> A named practitioner's first-person architecture account of a regulated-industry
> multi-agent security-ops platform (Falco → Kafka → Isolation Forest pre-filter →
> LangGraph/A2A agent fan-out on Kubernetes), whose transferable contributions are:
> safety constraints placed in **policy-as-code called at decision time, not in the
> reviewer's prompt**; a **classical anomaly model gating the LLM tier** with a
> runtime-tunable threshold and drift paging; and the framing of **escalation to a
> human and structural alerting as designed normal outputs** of the system.

## Source Context

- **Type**: blog-post (CNCF blog, derived from a KubeCon + CloudNativeCon Europe 2026
  talk; practitioner experience report).
- **Author credibility**: Willem Berroubache, Lead Security Architect at Orange
  Innovation (cloud native security architecture for Orange's 5G core), CNCF Golden
  Kubestronaut, selected for the 2026 Orange Expert Group in Security. The system is
  his own employer's internal platform: "an internal real-time security-operations
  platform protecting a regulated production environment, currently in active
  development with a rollout underway." High credibility for *what the team built and
  chose*; efficacy claims ("materially shorten mean time to detect and respond",
  "bounded" latency/token cost) are self-reported from a mid-rollout system with no
  benchmarks, scale figures, or failure data. No public repo is referenced.
- **Scope**: Covers five technical lessons (agent-as-workload, mTLS-without-mesh,
  policy-as-code safety, trace_id/GitOps observability, classical-ML gate), the
  human-in-the-loop protocol, the operational/alerting model, the three-team
  operating model, and a closing "Why this stack" section. Does NOT cover: any
  measured reliability/cost/latency/throughput numbers, post-rollout results,
  evaluation of agent answer quality, or what happens when OPA/Kyverno is
  unreachable. The "Why this stack" section is LF/CNCF-ecosystem advocacy —
  stack rationale is treated here as opinion; the operational mechanics are the
  extractable content (per Prospector caveat).

## Extracted Claims

### Claim 1: Each agent is deployed as its own Kubernetes Deployment — not an in-process module — so ordinary microservice mechanics (canary, HPA, isolation) apply, and the named failure mode of the single-process alternative is one agent's model-API timeout dragging the rest down
- **Evidence**: First-hand architecture description; the failure mode is asserted
  from experience, not from a postmortem or incident record.
- **Confidence**: emerging (a design argument from a mid-rollout system; no
  scale or incident data).
- **Quote**: "We deploy each agent as its own Deployment, with its own resource limits, identity, and restart policy."
- **Our assessment**: The mechanics are standard Kubernetes and the failure-isolation
  argument is sound for long-running serving agents: independent restart policy and
  resource limits are exactly what bounds a stuck retry loop. The stronger
  rhetorical claim ("The opposite pattern (all agents in one process) is faster to
  demo on a laptop and would be wrong in production") is workload-conditioned —
  see the tension with `blog-pagerduty-sre-agent-architecture` Claim 12 and
  `blog-linsun-pod-deployment-unit-ai-agent` under Contradicts. We buy the
  isolation property, not a universal deployment-unit rule.

### Claim 2: Inter-agent mTLS is delivered without a service mesh — cert-manager per-agent identities terminated at each agent's own gRPC/HTTP transport, plus CiliumNetworkPolicy restricting which agent identity may reach which MCP server
- **Evidence**: Stated topology choices with named projects; the "materially
  simpler" comparison is the author's judgment, with no mesh-operation cost data
  on either side.
- **Confidence**: emerging (argued position, contested-but-reasoned; the guide's
  corpus has no prior service-mesh-for-agents coverage to check it against).
- **Quote**: "The combination (cert-manager + agent-level mTLS + CiliumNetworkPolicy) is materially simpler than a mesh and gives us what a mesh would have given us."
- **Our assessment**: The mechanism is credible: mTLS at the transport with
  platform-issued identity plus identity-scoped network policy delivers the two
  properties a mesh would buy (transport encryption, per-identity reachability)
  without sidecars. What the claim does *not* cover is what a mesh also provides
  uniformly — traffic policy/telemetry at the sidecar, mTLS for non-gRPC legacy
  transports, identity rotation UX. Recorded as an argued position, not
  consensus. Note the threat-model framing that motivates it: "A2A messages carry
  proposed detection rules and response actions; the threat model says they are at
  least as sensitive as the data plane."

### Claim 3: Agent safety constraints belong in policy-as-code — OPA policies and Kyverno admission rules invoked by the reviewer agent over MCP for a deterministic verdict — not in the reviewer's system prompt, and the author flags this as the single change to make before any other
- **Evidence**: First-hand design of the system's action-gating path; the policy
  artifact is version-controlled, unit-tested, and code-reviewed. No failure
  data, red-team results, or comparison against a prompt-constrained reviewer.
- **Confidence**: emerging (a strongly-held, concretely-implemented design
  principle; unvalidated against attacks in the source).
- **Quote**: "The instinct is to put safety constraints in the reviewer’s system prompt. Don’t."
- **Our assessment**: This is the source's most transferable claim and it lands:
  prompt-reasoned safety constraints are nondeterministic, unversioned, untestable,
  and change silently when the model or prompt changes — a deterministic policy
  verdict is unit-testable and code-reviewable like any other artifact. The
  mechanics: "The reviewer calls into OPA via MCP, gets a deterministic verdict,
  and acts. The reviewer’s prompt itself is short and, frankly, boring." And: "The
  policy is version-controlled, unit-tested, and code-reviewed like any other
  artefact. If there is one change to make before anything else, it is this one."
  The gap the source does **not** address: OPA-over-MCP is now on the agent's
  decision path, so an OPA outage has to have fail-open/fail-closed semantics —
  the exact availability-dependency question Ch05 already documents for
  gateway-attached guardrails (`docs-litellm-generic-guardrail-api`, Claims 8–10).
  The source is silent; the guide should apply the same framing rather than assume
  the deterministic verdict is always available.

### Claim 4: The reviewer receives structured input, not free-form LLM prose — a threat-analyst agent classifies each escalation against MITRE ATT&CK upstream of the safety verdict
- **Evidence**: Stated pipeline position (threat-analyst agent → structured
  classification → reviewer); no classification accuracy data.
- **Confidence**: emerging (concrete design; unmeasured).
- **Quote**: "Upstream of the reviewer, a threat-analyst agent classifies each escalation against the MITRE ATT&CK framework, so the reviewer gets a structured input rather than free-form LLM prose."
- **Our assessment**: Good layering: the safety decision consumes a fixed schema
  keyed to an external taxonomy, which shrinks the input surface the policy engine
  has to reason about and makes policy tests writable against known shapes. Pairs
  with Claim 3 — structured input is what makes a short, "boring" reviewer prompt
  viable.

### Claim 5: A classical anomaly model gates the LLM tier — a scikit-learn Isolation Forest scores 17 features in microseconds, and only samples above a calibrated threshold reach agent fan-out, bounding both per-event latency and token cost
- **Evidence**: Architecture description with named algorithm, feature count, and
  qualitative timing ("microseconds"); no latency percentiles, token accounting,
  or cost figures.
- **Confidence**: emerging (the mechanism is sound and checkable in principle;
  the "bounded" outcome is asserted, not measured).
- **Quote**: "A scikit-learn Isolation Forest sits in front of the agents, scoring each sample in microseconds on 17 features; only samples above a calibrated threshold reach the agent fan-out."
- **Our assessment**: Buy the pattern: it is the corpus's clearest example of
  *pre-filtering telemetry with a cheap deterministic model so the LLM only sees
  the genuinely novel slice* — and it independently matches Google's guidance
  against using LLMs where a small specialist model fits
  (`docs-google-sre-prodcast-04-09-ai-agents`, Claim 15). The framing to preserve
  is economic as much as technical: "If every event triggered the full agent
  fan-out, the LLM tier would dominate the platform’s economics." The explicit
  outcome claim: "Per-event latency and token cost both stay bounded, and sizing
  the LLM tier becomes normal capacity planning." No numbers back "bounded" —
  record as design intent.

### Claim 6: The gate's threshold is a runtime policy parameter consulted at decision time (tightenable under load without redeploying agents), feature-distribution drift is itself a paged Prometheus metric, and the model retrains weekly by design
- **Evidence**: Stated operational loop with named metric type (paged) and
  retrain cadence; no drift incidents, page volume, or threshold-tuning history.
- **Confidence**: emerging (specific, checkable operational design; no
  operational record).
- **Quote**: "The Isolation Forest retrains weekly by design, and feature-distribution drift is itself a paged Prometheus metric."
- **Our assessment**: This is the half of the pattern most worth stealing: the
  gate is treated as a *monitored dependency with a lifecycle*, not a set-and-
  forget heuristic. Paging on feature-distribution drift means the pre-filter's
  own blind spot becomes an alert rather than silent misclassification. The
  threshold-as-policy detail: "The anomaly threshold is not a static constant. It
  is a policy parameter the reviewer consults at decision time. We can tighten it
  under load without redeploying agents." Caveat the source skips: tightening a
  threshold under load raises the LLM-invocation fraction *only if* the threshold
  moves the other way — the operational knob's failure direction (too tight =
  more LLM cost; too loose = missed detections) and its calibration process are
  not described.

### Claim 7: Observability rides a trace_id carried in every A2A task envelope, and that propagation cut one real decision-reconstruction exercise from a day to fifteen minutes
- **Evidence**: One concrete walkthrough during development: all entries for the
  trace_id pulled and lined up to present an automated decision to an internal
  stakeholder. Single anecdote, self-reported.
- **Confidence**: anecdotal for the fifteen-minutes-vs-a-day figure; emerging for
  the underlying propagation design (structured JSON logs with trace_id, agent
  identity, MCP calls, token usage; Prometheus per-agent metrics; Hubble flow
  view).
- **Quote**: "The whole reasoning chain walked through in about fifteen minutes. Without trace_id propagation through A2A, it would have been a day."
- **Our assessment**: Buy the mechanism — a correlation key on the inter-agent
  protocol envelope is the only way to reassemble a multi-agent decision chain,
  and this is the corpus's first *outcome* measurement for doing so (even if
  n=1). It is the concrete payoff for Ch02's rule that correlation survives an
  agent hop only if the hop re-sends it (`docs-litellm-a2a-agent-gateway`,
  Claim 2, documents the header-forwarding obligation; this source documents the
  envelope-level version and the operational result when it is threaded). The
  design also enumerates the scraped surface: "Prometheus scrapes per-agent
  metrics (request rates, MCP-call latency, reviewer auto-execute / auto-reject /
  escalate ratios)."

### Claim 8: Every agent's system prompt, tool list, and output schema is a Kubernetes Custom Resource reconciled by Argo CD from Git, with the reviewer's policy bundle in the same repo, so promoting a change is a pull request — code-reviewed, audited, reversible
- **Evidence**: Stated delivery mechanism; the failure mode it prevents is
  described vividly but without an incident example from this system.
- **Confidence**: emerging (concrete, standard toolchain; asserted benefits).
- **Quote**: "Every agent’s system prompt, tool list, and output schema is a Kubernetes Custom Resource, reconciled by Argo CD from Git."
- **Our assessment**: This is the strongest extension in the corpus of the
  GitOps-for-agent-configuration thread: not just weights/RBAC/prompts in Git
  (`blog-cncf-cluster-aware-ai-agent-argo-gitops`, Claim 4) but the *decision
  policy* living in the same reviewed repo — one change surface for behavior and
  safety. The two supporting sentences worth carrying into the guide: "Promoting a
  change is a pull request: code-reviewed, audited, reversible." and "This is where
  most early multi-agent deployments fall over: prompts scattered across notebooks
  and config files until the day an agent surprises someone." Open question the
  source doesn't answer: CR-reconciled prompts mean Argo CD is on the behavior
  change path — drift between Git and cluster, and a bad policy-bundle PR, now
  propagate through reconciliation (admission-rejected policy bundles are
  themselves alerted on — see Claim 10).

### Claim 9: Escalation to a human is a designed normal output with three terminal states — auto-execute, auto-reject, or escalate — firing on low reviewer confidence, an always-escalate asset list, or a configured blast-radius limit, and the escalation decision is a deterministic versioned policy verdict with its own SLO and dashboards
- **Evidence**: Stated protocol and trigger list; escalation routing is to a
  Mattermost SOC channel with inline ChatOps approve/dismiss/investigate commands.
  No escalation-rate data (though Claim 7 notes the reviewer's auto-execute /
  auto-reject / escalate ratios are scraped).
- **Confidence**: emerging (a fully specified design from a mid-rollout system).
- **Quote**: "It is designed to fire in three cases: reviewer confidence falls below threshold; the asset is on an always-escalate list (control-plane components, identity stores, anything customer-facing or compliance-sensitive); or the proposed action would exceed a configured blast radius."
- **Our assessment**: Three details are novel for the corpus: (1) escalation as
  "a normal output of the reviewer", not an error path; (2) **blast radius as an
  escalation trigger** — a geometric limit on action size rather than an asset
  class or confidence score, which is the first corpus example of sizing-based
  human gating; (3) the escalation decision itself being a versioned policy with
  an SLO ("'Should this case escalate?' is a deterministic policy verdict,
  version-controlled in Git, with its own SLO and dashboards. It is not a question
  of which analyst is on shift") — HITL coverage as an *engineering* property
  independent of rota staffing. The closing diagnosis is quotable guide material:
  "If your HITL story is “we’ll add an approval step later”, or “the analyst can
  always intervene”, you don’t really have one yet."

### Claim 10: Alerts are structural, not behavioural — page on failed policy-bundle admission, MCP p99 latency, pre-filter drift, and A2A queue depth rather than "agent X gave a weird answer", and handle agent regressions exactly like microservice regressions (roll back the CR via Argo CD, ticket, GitOps fix)
- **Evidence**: The alert vocabulary is listed explicitly; the regression
  workflow is described as the team's practice. No alert examples, MTTR data, or
  comparison against a behavioural-alerting approach.
- **Confidence**: emerging (specific and actionable; unmeasured).
- **Quote**: "Alerts are structural: policy bundle failed admission, MCP server p99 latency, anomaly-pre-filter drift, A2A queue depth above watermark. Not “agent X gave a weird answer”."
- **Our assessment**: Buy the split completely — every listed signal is a
  machine-checkable property of the *pipeline*, whereas "gave a weird answer" has
  no threshold and pushes you into LLM-as-judge alerting with all its calibration
  problems. The operational payoff is stated bluntly: "When an agent regresses
  during iteration, we treat it like any production microservice regression: roll
  back the Custom Resource via Argo CD, open a ticket, ship a fix through GitOps.
  No special agent-incident runbook to invent, and that is the point." Note the
  dependency: this works *because* of Claim 8 (behavior is a CR, so rollback is a
  reconciliation op). The behavioral layer is not abandoned — it is handled by
  eval/spot-audit rather than paging ("Engineers will curate the reviewer’s safety
  policy and spot-audit deployed rules instead of writing them").

### Claim 11: Three teams (SOC, platform, small AI engineering) coordinate through narrow machine-readable contracts — CRDs, OPA bundles, A2A schemas — and the operational goal is capacity, not just speed: scaling detection coverage means deploying agent replicas and tightening the policy bundle instead of hiring analysts
- **Evidence**: Ownership description plus the stated intent; headcount/capacity
  outcome is asserted, not measured (system mid-rollout).
- **Confidence**: emerging (organizational design; no outcome data).
- **Quote**: "We deliberately kept the contracts between them narrow and machine-readable (CRDs, OPA bundles, A2A schemas), so a change in one area never depends on a meeting in another."
- **Our assessment**: The contract-as-artifact ownership model is a clean,
  transferable answer to the cross-team coordination problem: each team's interface
  is a reviewable artifact with its own repo lifecycle. The capacity claim —
  "Scaling detection coverage used to mean hiring more analysts to write more
  rules. With the agent layer, it means deploying more agent replicas and
  tightening the reviewer’s policy bundle" — is the article's most consequential
  assertion and the least supported; record it as intent, not result. The
  recognition that rule authorship was "the structural bottleneck for years" is
  good context for why this architecture exists at all.

### Claim 12: The protocols (A2A, MCP) are treated as the durable interfaces and the agent runtime as a revisitable choice — most agents run LangGraph, some are framework-free where state machines/retry semantics/tool-call sequencing need tighter control
- **Evidence**: Stated team practice and rationale; no framework comparison data.
- **Confidence**: emerging (architecture posture, reasoned).
- **Quote**: "The protocols (A2A, MCP) are what we treat as the durable interfaces; the runtime is a choice we can revisit."
- **Our assessment**: The right layering bet and worth stating in the guide: put
  your durability in protocol standards with neutral governance (A2A under the LF,
  MCP under the Agentic AI Foundation) and keep the runtime swappable. The
  hand-written-without-framework detail ("for some of our agents we deliberately
  keep the logic hand-written without any framework at all when we want full
  control over state machines, retry semantics, and tool-call sequencing") echoes
  the corpus's recurring instruction to drop the framework where determinism
  matters, and pairs with the short-and-boring reviewer prompt of Claim 3.

## Concrete Artifacts

System pipeline and topology — verbatim from the article's intro and Figure 1
caption (https://www.cncf.io/blog/2026/06/17/why-cloud-native-belongs-at-the-heart-of-agentic-ai-lessons-from-building-a-multi-agent-security-platform-on-kubernetes):

```
Falco with eBPF intercepts every syscall on the workloads we monitor; events
flow through Kafka into an Isolation Forest classical anomaly model that
pre-filters in front of the LLM-driven agents.

Figure 1: System overview. A Coordinator Agent (LangGraph + A2A) orchestrates
four specialised agents: Detect (Falco + ML), Analyse (Threat Analyst),
Remediate, and Notify (Mattermost), plus a Human-in-the-Loop branch and a
feedback loop that retrains the anomaly model. Adapted from my talk at KubeCon +
CloudNativeCon Europe 2026.
```

Decision pipeline (Claims 3, 4, 9), condensed from the article's own sequence —
attribution: same article, sections 3 and "Keep the human in the loop":

```
event (Falco eBPF → Kafka) → Isolation Forest score (17 features, µs)
  → above threshold? → agent fan-out (Detect / Analyse / Remediate / Notify,
    coordinated by Coordinator Agent via A2A)
      → threat-analyst agent classifies vs MITRE ATT&CK (structured input)
        → reviewer agent calls OPA via MCP → deterministic verdict
          → auto-execute | auto-reject | escalate (Mattermost + ChatOps)
escalation fires on: reviewer confidence < threshold; asset on always-escalate
list (control-plane components, identity stores, customer-facing /
compliance-sensitive systems); proposed action exceeds configured blast radius.
```

Structural alert set — verbatim (Claim 10):

```
Alerts are structural: policy bundle failed admission, MCP server p99 latency,
anomaly-pre-filter drift, A2A queue depth above watermark. Not “agent X gave a
weird answer”.
```

Three-team contract boundaries (Claim 11), verbatim:

```
Three groups touch this system every week: the SOC, who own detection outcomes
and the reviewer’s safety policy; the platform team, who own the cluster,
GitOps pipeline, and agent runtime; and a small AI engineering group, who own
the agent contracts and the anomaly model.
```

Observability surface (Claim 7), verbatim:

```
Agents emit structured JSON logs with the trace_id, the agent identity, the MCP
calls made, and the LLM token usage. Prometheus scrapes per-agent metrics
(request rates, MCP-call latency, reviewer auto-execute / auto-reject / escalate
ratios). Cilium Hubble gives the flow view when the question is “did the right
pod reach the right service”.
```

Note: the article ships no manifests, config files, or policy examples — the
concrete artifacts are the pipeline description, the alert vocabulary, and the
trigger/terminal-state lists above.

## Cross-References

**Candidates from `miner-related-notes.md` (all ten listed paths evaluated;
four cited, six dismissed):**

- `source-notes/docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**:
  retail/gaming SLO granularity and migration practice; no agent-architecture or
  policy content.
- `source-notes/docs-google-sre-prodcast-03-13-imperative-declarative.md` —
  **cited** (Extends): **Claim 4** ("The declarative alternative — components
  each contribute a *part* of one intended-state document, which the system
  combines and rolls out under policy") is the change-management frame for this
  source's prompts/tool-lists/output-schemas-as-CRs (Claim 8): each agent's
  behavior is one component contributing to the intended state Argo CD rolls out,
  and the reviewer's policy bundle shares the same document. **Claim 14** adds
  that a declarative model can "enforce policies/invariants automatically, so a
  new person can't trigger an outage by violating a rule that previously lived
  \"in people's brains\"" — the same benefit this source claims for Kyverno
  admission rules on the agent layer.
- `source-notes/blog-pagerduty-sre-agent-architecture.md` — **cited**
  (Extends, with a documented tension): the nearest multi-agent SRE-system
  neighbour in the corpus. **Claim 12** ("IO-bound agentic workloads do not
  benefit from service boundaries...") is in tension with this source's Claim 1
  — see Contradicts below. On the shared ground: both systems put a coordinator
  in front of specialised sub-agents, and this source's Claim 7 reviewer-ratio
  metrics and PagerDuty's investigation-loop engineering are two answers to
  operating that shape in production.
- `source-notes/docs-google-sre-ai-engineering-reliable-operations.md` —
  **cited** (Corroborates): **Claim 2** (Safety Trifecta — Transparency,
  Real-time Risk Evaluation, Progressive Authorization) and especially **Claim 5**
  (Actus, "a decoupled actuation control plane that serves as the safety gateway
  for all autonomous production changes") are Google's version of this source's
  core placement rule: the safety verdict is produced *outside* the acting model,
  in a dedicated deterministic component. **Claim 4** ("No ambient access &
  least privilege — agent identities must be distinct from humans, strongly
  authenticated") corroborates the per-agent cert-manager identities of Claim 2.
- `source-notes/docs-google-sre-configuration-specifics.md` — **cited**
  (Corroborates): **Claim 12** ("Treat configuration as code"; "check config
  into source control for history, rollback, and code review") is the general
  configuration discipline this source instantiates specifically for safety
  policy ("version-controlled, unit-tested, and code-reviewed like any other
  artefact", Claim 3).
- `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` —
  **dismissed**: Python-SDK eval tracing bridge; no overlap with deployment
  topology, policy placement, or gate design.
- `source-notes/docs-litellm-batches-api.md` — **dismissed**: batch rate-limit
  accounting; the shared "bound the LLM tier's economics" theme is too loose to
  be an evidential cross-ref (this source's cost control is pre-filtering, not
  quota accounting).
- `source-notes/failure-litellm-supply-chain-compromise-march-2026.md` —
  **dismissed**: supply-chain compromise of a gateway package pipeline; no
  shared claim (the only adjacent surface — GitOps/CI credentials — is not
  raised by this source).
- `source-notes/docs-google-sre-prodcast-03-01.md` — **dismissed**: SRE
  methodology, org dynamics, and observability adoption; no agent-architecture
  content.
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **dismissed**:
  within-request model composition via the gateway; unrelated to any claim here.

**Additional cross-references found by searching `source-notes/` beyond the
candidate list:**

- **Corroborates**:
  - `blog-cncf-network-boundary-ai-agents-nginx-otel` **Claim 1** (the boundary
    must be "a property of the architecture, not a policy we hope the application
    respects") — same thesis at a different layer: that source enforces agent
    *egress* at the network (forward proxy + iptables), this source enforces
    agent-to-MCP reachability via CiliumNetworkPolicy plus transport-level mTLS
    (Claim 2). Both are "enforcement lives below the model" arguments; this
    source adds the safety-verdict layer (Claim 3) that the network-boundary
    note explicitly says its layer cannot supply (**its** Claim 4: "Restricting
    where an agent can communicate does not guarantee that its decisions are
    correct or safe"). Complementary halves.
  - `docs-google-sre-prodcast-04-09-ai-agents` **Claim 15** ("do NOT use LLMs
    where a regex or a small specialist model fits") — with the heading's
    stated example that anomaly detection on a time series is better served by
    a classic method — is Google's rule; this source's Isolation Forest gate
    (Claim 5) is that rule implemented as an architecture with a tunable
    threshold (Claim 6). Also **Claim 3** (default guardrail denies
    world-mutating actions pending explicit human permission) aligns with
    Claim 9's escalate-as-normal-output design.
  - `blog-cncf-4-body-problem-sre-context` **Claim 4** ("Every agent action
    requires a durable decision trace") — recording inputs, policies in effect,
    model version, rejected hypotheses, action, and outcome — and **Claim 9**
    (the knowledge graph must be versioned so decisions replay against the exact
    snapshot) — this source's trace_id walkthrough (Claim 7) is a working
    implementation of decision tracing on the A2A envelope, and its
    fifteen-minute reconstruction is the operational payoff for that note's
    failure mode "unreconstructable reasoning" (**its** Claim 8).
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry` **Claim 6**
    (multi-agent systems need distinct agent names per sub-agent and explicit
    handoff spans) — this source's structured JSON logs carrying "the trace_id,
    the agent identity, the MCP calls made, and the LLM token usage" (Claim 7)
    is the emitting side of that contract.
  - `docs-google-sre-configuration-specifics` **Claim 12** — see candidates
    above.
- **Extends**:
  - `blog-cncf-cluster-aware-ai-agent-argo-gitops` **Claim 4** ("Prompts, model
    selection, and RBAC live in Git. Argo CD reconciles them. The agent's
    behavior is auditable through `git log`.") — this source extends that
    GitOps-for-agent-configuration pattern from prompts/RBAC to *tool lists,
    output schemas, and the safety policy bundle* (Claim 8), and adds the
    regression-handling consequence: rollback of a behavior change is an Argo CD
    reconciliation, so agent incidents use the microservice playbook (Claim 10).
    That note's caution that `git log` audits config, not runtime behavior,
    applies equally here.
  - `docs-litellm-a2a-agent-gateway` **Claim 2** (trace grouping and per-agent
    spend attribution are a manual forwarding obligation, silent when skipped) —
    this source is the protocol-envelope counterpart: the A2A envelope itself
    carries the `trace_id` ("The A2A envelope carries a trace_id with every
    task; that trace_id is what holds our observability together"), which
    removes the header-forwarding footgun *if* every implementation honours the
    envelope. Guide-relevant pairing: one note states the obligation and its
    silent failure, the other shows the design and the payoff (Claim 7).
  - `docs-litellm-generic-guardrail-api` **Claims 8–10** (fail-open/fail-closed
    spectrum for guardrails on the request path; fail-on-error false is a
    complete bypass) — the availability-dependency framing this source's
    OPA-over-MCP verdict path (Claim 3) needs and does not provide: the article
    never says what the reviewer does when OPA is unreachable. Not a
    contradiction — a gap. Ch05's existing "A guardrail in the request path is
    an availability dependency" section should be explicitly generalized to
    decision-time policy verdicts.
  - `blog-cncf-policy-engine-offline-production-fidelity` **Claim 6** ("The
    point of offline testing is that it should be *identical* to what runs in
    the cluster") — the other half of a policy-as-code safety layer: this
    source places enforcement in OPA/Kyverno (Claim 3); that note covers making
    the policy's *evaluation* trustworthy before it ships. A guide treatment of
    "safety as policy" needs both placement (here) and test fidelity (there).
- **Contradicts**: two tensions examined; **no contradiction issue filed** (both
  resolved as conditioning variables per MINER.md §4a):
  1. `blog-linsun-pod-deployment-unit-ai-agent` **Claim 2** / its central thesis
     (Pod-per-agent solved five problems but is the wrong *deployment* unit for
     idle agents; multiplex logical agents onto a fixed worker pool) vs this
     source's Claim 1 (each agent is its own Deployment — "The opposite pattern
     (all agents in one process) is faster to demo on a laptop and would be
     wrong in production"). The conditioning variable is **agent duty cycle**:
     Lin Sun's agents "may wake up only when assigned a task, execute
     for a few seconds or minutes, and then become completely idle" (that
     note's Claim 3), whereas this source's agents are
     continuously-serving security-ops workers whose independent restart/resource
     isolation is the point. Both designs are defensible under their own
     condition; neither source argues the other's condition away. Recorded here
     so the Smith writes a duty-cycle-conditioned deployment-unit rule rather
     than a universal one.
  2. `blog-pagerduty-sre-agent-architecture` **Claim 12** ("spreading IO-bound
     agents across services buys operational complexity — deployment, service
     discovery, network failure modes, distributed tracing — without buying the
     thing services are for") vs this source's Claim 1. Conditioning variable is
     **workload class and failure-isolation need**: PagerDuty's IO-bound
     investigation sub-agents share one team and one supervisor; this source's
     agents sit on independent model-API call paths where one stuck retry loop
     must not consume the fleet's resources ("One agent stuck on a model-API
     timeout drags the rest down"). The guide has no current single-process-vs-
     distributed rule to contradict, and each source's evidence is self-reported
     for its own system — below the bar for a contradiction issue.
  Checked `CONTRADICTIONS.md` and open `contradiction`-labeled issues: no
  existing entry covers deployment unit or safety-constraint placement.
- **Novel** (new to the corpus):
  - The first source to state the **safety-constraints-are-policy-not-prompt**
    placement rule outright, with a working mechanism (OPA via MCP →
    deterministic verdict; policy unit-tested and code-reviewed) and an explicit
    priority ranking ("If there is one change to make before anything else, it is
    this one").
  - The first **classical-ML pre-filter gating an LLM agent tier** in production:
    Isolation Forest over 17 features, threshold as a runtime policy parameter,
    feature drift as a paged metric, weekly retrain — a cost/latency control
    distinct from the corpus's routing/caching patterns.
  - **Blast radius as an escalation trigger** for human-in-the-loop — sizing-based
    gating alongside confidence and asset class, with escalation itself carrying
    an SLO (Claim 9).
  - **Structural-vs-behavioural alerting** as an explicit doctrine for agent
    systems, plus the "no special agent-incident runbook" regression claim
    (Claim 10).
  - A **deliberate no-service-mesh agent topology** (cert-manager identities +
    transport-level mTLS + CiliumNetworkPolicy) — a contested position the corpus
    has not previously covered either way (Claim 2).
  - The **three-team narrow-contract operating model** (SOC / platform / AI eng
    over CRDs, OPA bundles, A2A schemas) as ownership-boundary material
    (Claim 11).

## Guide Impact

- **Chapter 06 (Security and Trust)**: In `### Function-calling authorization`
  and the trust-boundary material, add the placement rule from Claims 3–4:
  *the safety verdict for a consequential action should be a deterministic
  policy decision produced outside the acting model (OPA/Kyverno at decision
  time), not a constraint reasoned about in the reviewer's system prompt* — cite
  this source for the rule and its mechanism, and Google's Actus
  (`docs-google-sre-ai-engineering-reliable-operations`, Claim 5) as the
  independent corroborating design. State what the prompt-based alternative
  loses: determinism, version history, unit tests, code review. Also record the
  structured-input precondition (MITRE ATT&CK classification upstream of the
  verdict, Claim 4) — a short boring reviewer prompt works because its input is
  a schema, not prose.

- **Chapter 05 (LLM Ops Reliability)**: Extend `### A guardrail in the request
  path is an availability dependency` (`guide/05-llm-ops-reliability.md:1307`)
  beyond gateway hooks: a policy engine called by the agent over MCP (this
  source's Claim 3) is the *same class* of dependency, and the source does not
  say what happens on OPA unreachability — recommend applying the existing
  fail-open/fail-closed + guardrail-error-SLO rules to decision-time policy
  verdicts. Additionally, add the pre-filter gate (Claims 5–6) to the LLM-ops
  cost/latency material: *bound the agentic path's economics with a cheap
  deterministic pre-filter whose threshold is a runtime policy parameter and
  whose feature drift is a paged metric* — distinct from routing and caching,
  and corroborated by `docs-google-sre-prodcast-04-09-ai-agents` Claim 15.

- **Chapter 02 (Observability)**: Under `### Correlation survives an agent hop
  only if the hop re-sends it` (`guide/02-observability.md:83`), add the
  protocol-envelope variant: the A2A envelope carrying `trace_id` per task
  (Claim 7) is the design that removes the header-forwarding footgun documented
  in `docs-litellm-a2a-agent-gateway` Claim 2, and the fifteen-minutes-vs-one-day
  decision reconstruction is the outcome evidence for the rule. Add the reviewer
  ratio metrics (auto-execute / auto-reject / escalate) as a recommended
  dashboard surface, and the structural alert list (Claim 10) to the
  anomaly/alerting section as agent-specific signal dimensions: policy-bundle
  admission failures, MCP p99, pre-filter drift, A2A queue depth.

- **Chapter 03 (Runbooks and Agents)**: Add, near the GitOps/rollback material,
  the rule from Claims 8 and 10: *prompts, tool lists, output schemas, and
  safety policy are Kubernetes CRs reconciled from Git, so an agent regression is
  rolled back exactly like a microservice regression — no special agent-incident
  runbook* — extending `blog-cncf-cluster-aware-ai-agent-argo-gitops` Claim 4.
  Record the operational precondition: because behavior rolls out through Argo CD,
  a bad policy-bundle PR propagates by reconciliation, which is why
  admission-rejection of the bundle is itself a structural alert.

- **Chapter 04 (On-call and Toil)**: For ownership-boundary material, add the
  three-team narrow-contract model (Claim 11) — SOC owns detection outcomes and
  the safety policy, platform owns cluster/GitOps/runtime, AI engineering owns
  agent contracts and the anomaly model, with CRDs/OPA bundles/A2A schemas as
  the interfaces — and carry the capacity claim ("deploying more agent replicas
  and tightening the reviewer's policy bundle" instead of hiring analysts) as
  *intent from a mid-rollout system*, explicitly unvalidated.

## Extraction Notes

- Source read in full: single CNCF blog page (article body ~21 KB of extracted
  text; intro, five lessons, HITL section, rollout/teams sections, "Why this
  stack", author bio). No sub-pages were substantive: the linked KubeCon talk
  (YouTube) and the author's LinkedIn were not fetched — they are presentations
  of the same material, and the article is the canonical write-up. Figure 1's
  image was not OCR'd; its caption (part of the page text) is quoted as an
  artifact.
- **Quote fidelity**: every `Quote` and quoted artifact passage was verified
  character-for-character against the fetched page text before writing (smart
  quotes, `trace_id` underscores, and the source's British spellings —
  "artefact", "specialised" — preserved). Where the page renders emphasis
  (e.g. **Argo CD**, **cert-manager**) inside a sentence, the quoted fragment
  reproduces the text without markup; no non-adjacent sentences were spliced.
- **Evidence caveats recorded per Prospector**: self-reported from a system
  "currently developing and rolling out"; no benchmark numbers, deployment
  scale, throughput, error rates, or post-rollout results anywhere in the
  article; no public repo. The "Why this stack" section is LF/CNCF advocacy
  (including a procurement-governance argument) and is treated as opinion —
  only the operational mechanics are extracted as claims.
- **`miner-related-notes.md` disposition**: all ten candidate paths evaluated —
  four cited (`docs-google-sre-prodcast-03-13-imperative-declarative`,
  `blog-pagerduty-sre-agent-architecture`,
  `docs-google-sre-ai-engineering-reliable-operations`,
  `docs-google-sre-configuration-specifics`) and six explicitly dismissed (see
  Cross-References). Additional cross-refs (`docs-google-sre-prodcast-04-09-ai-agents`,
  `blog-cncf-network-boundary-ai-agents-nginx-otel`,
  `blog-cncf-4-body-problem-sre-context`, `blog-honeycomb-instrumenting-ai-agents-opentelemetry`,
  `blog-cncf-cluster-aware-ai-agent-argo-gitops`, `docs-litellm-a2a-agent-gateway`,
  `docs-litellm-generic-guardrail-api`, `blog-cncf-policy-engine-offline-production-fidelity`,
  `blog-linsun-pod-deployment-unit-ai-agent`) were found by searching
  `source-notes/`. Every cited `Claim N` was re-read and verified against the
  named note per MINER.md §4b.
- **No contradiction issue filed**: the two tensions (deployment unit vs
  `blog-linsun-pod-deployment-unit-ai-agent` and `blog-pagerduty-sre-agent-architecture`)
  are duty-cycle/workload-class conditioning variables under MINER.md §4a, and
  the guide currently states no opposing rule; `CONTRADICTIONS.md` and open
  `contradiction` issues were checked for existing entries. The OPA-unreachable
  question is a *gap*, not a conflicting claim. Rationale is written out under
  Cross-References → Contradicts so the Assayer can overrule if they disagree.
- `date_extracted` / `last_checked` set to 2026-10-16 UTC (page re-fetched and
  quote-verified on that date). `confidence_overall: emerging` — mechanics are
  concrete and quotable, but the source is self-reported mid-rollout with zero
  quantitative validation; no claim here reaches `settled`, and Claim 7's
  fifteen-minute figure is graded `anecdotal`.
- No `guide/` edits, no `registry/*` edits: registry indexes are rebuilt after
  merge from this note's frontmatter and claim headings.
