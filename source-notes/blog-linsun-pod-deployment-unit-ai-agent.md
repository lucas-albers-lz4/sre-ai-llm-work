---
source_url: https://www.cncf.io/blog/2026/07/14/is-a-pod-the-right-deployment-unit-for-an-ai-agent
source_type: blog-post
title: "Is a Pod the right deployment unit for an AI agent?"
author: "Lin Sun (Solo.io, CNCF Ambassador)"
date_published: 2026-07-14
date_extracted: 2026-10-03
last_checked: 2026-10-03
status: current
confidence_overall: emerging
issue: "#1570"
---

# Is a Pod the right deployment unit for an AI agent?

> A CNCF blog architecture argument (plus the `agent-substrate` project's own
> docs) that the Kubernetes Pod is likely still the right *execution* unit for AI
> agents but no longer the right *deployment, identity, or lifecycle* unit —
> because agents are idle most of the time — and that a control plane
> (`WorkerPool` / `ActorTemplate` / `Worker` / `Actor`) above Kubernetes is
> needed to multiplex many logical agents onto a fixed pool of Pods. Contributes
> the corpus's first concrete artifacts for agent deployment-unit choice, actor
> identity as a scheduling-independent correlation key, and the observability /
> cardinality / egress-policy consequences of breaking the Pod↔agent 1:1 tie.

## Source Context

- **Type**: blog-post (CNCF blog). Architecture-positioning post with embedded
  CRD manifests and CLI transcripts.
- **Author credibility**: Lin Sun, Solo.io, CNCF Ambassador. Solo.io is the
  creator of `agentgateway` and a co-founder of the `agent-substrate` project;
  `kagent` is the CNCF Sandbox project built on `agent-substrate`. So the author
  is the project's own architect arguing for the project's own abstraction —
  first-hand knowledge of the design, real conflict of interest on the
  "one Pod per agent was wrong" conclusion. Credibility is high for *what the
  CRDs and controllers actually do* (the artifacts are checkable) and low for
  *whether Pod-per-agent is the wrong call in general*.
- **Scope**: Covers (1) the three-stage evolution of kagent's agent runtime,
  (2) `WorkerPool` / `ActorTemplate` CRD YAML, (3) `kubectl-ate get workers` /
  `get actors` output, (4) the argument that Pod is the wrong deployment /
  identity / lifecycle unit, (5) four open questions (identity, security and
  policy, ownership and multi-tenancy, observability). Does **NOT** cover:
  benchmarks, latency or cost numbers, density methodology, failure /
  postmortem material, migration guidance from a Pod-per-agent deployment, or
  what happens when a worker dies mid-actor.
- **Linked pages followed for extraction** (per MINER.md §1, all linked from the
  article):
  1. `https://github.com/agent-substrate/substrate` README — the project's own
     density and resume-latency figures, oversubscription demo numbers,
     component tour, pre-1.0 status, worker-capacity node-label version skew.
  2. `https://raw.githubusercontent.com/agent-substrate/substrate/main/docs/observability.md`
     — how "observability follows the logical agent" is actually implemented
     (`ate.*` identity metadata, the cardinality rule that bars actor identity
     from metric labels, the anti-spoofing drop rule, and three concrete
     attribution gaps).
  3. `https://raw.githubusercontent.com/agent-substrate/substrate/main/docs/request-parking.md`
     — what happens on worker-pool saturation (bounded park + admission lot
     instead of a bare `503`).
  4. `http://agentgateway.dev` — the gateway the article proposes for
     policy mediation (Solo.io project, A2A/MCP/LLM data plane).
  - `https://kagent.dev/docs/kagent/examples/agent-substrate` (the article's
    primary "learn more" link) returned **HTTP 500** and could not be read.
  - The Christian Posta LinkedIn post on agent identity linked from the
    article's identity section is a LinkedIn `/pulse/` URL that could not be
    fetched; it is cited by the article as a pointer, not quoted.

## Extracted Claims

### Claim 1: One shared runtime hosting many agents was kagent's first architecture, and it worked for demos but broke down as agent count grew — the isolation, identity, policy, per-agent visibility and ownership questions it raised are "agent platform questions," not Kubernetes questions
- **Evidence**: The author's own retrospective on kagent's stage 1. No metrics;
  the artifact is the enumerated list of five questions that forced the redesign.
- **Confidence**: settled (the author built it; this is a factual history of
  their own system)
- **Quote**: "It was the simplest architecture possible: one runtime hosting many agents."
- **Quote**: "These aren’t Kubernetes questions. They’re agent platform questions."
- **Our assessment**: The five-question list (isolate agents from each other,
  per-agent identity, access and network policy enforcement, understand what an
  individual agent is doing, ownership and multi-tenancy) is the most reusable
  part of this post. It is a checklist any team can run against its own
  single-runtime agent host, and it is the same list that reappears in the
  article's "Challenging More Than Deployment Model" section — the second
  attempt (Pod-per-agent) answered all five, and paid for it in density. We buy
  the framing. We do not read the first stage as a strawman: a shared runtime is
  genuinely the cheapest thing to build, and Solo.io shipped it.

### Claim 2: Pod-per-agent (Pod + Service + ServiceAccount) bought isolation, native identity, unchanged network/admission/security controls, per-agent log/metric/trace attribution, and Kubernetes-native scheduling — all in one decision
- **Evidence**: The author's assessment of their own stage-2 architecture. No
  before/after numbers, but each claim is a specific Kubernetes mechanism with a
  named object (`ServiceAccount`, network policy, admission policy).
- **Confidence**: settled (these are standard Kubernetes properties, and the
  author had them running)
- **Quote**: "A Pod provides process and container isolation. A ServiceAccount gives every agent its own Kubernetes identity, allowing us to integrate naturally with authentication and authorization mechanisms. Existing network policies, admission policies, and security controls continue to work without modification. Observability systems can attribute logs, metrics, and traces to individual agents. Scheduling and resource management also became Kubernetes-native."
- **Our assessment**: This is the strongest argument *for* the status quo and the
  guide should carry it as the default recommendation: for long-lived,
  continuously-available agents, one Pod + Service + ServiceAccount per agent
  remains correct, because every one of those five properties is free. Note the
  qualifier the article itself does not put in this paragraph — "Observability
  systems can attribute logs, metrics, and traces to individual agents" is
  *mechanism-level* attribution (the Pod is the identity), which is not the same
  as application-level attribution of a logical agent's execution chain; see
  Claim 11 and `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
  Claim 2 / Claim 4 for the other half.

### Claim 3: Agents break the assumption that underpins the Pod-as-deployment-unit model: a service is expected to be continuously available, an agent "may wake up only when assigned a task, execute for a few seconds or minutes, and then become completely idle"
- **Evidence**: The author's stated reasoning, plus four enumerated agent
  execution patterns that have no microservice analogue: on-demand subagent
  fan-out, impersonating a user / acting on a human's behalf, pausing for human
  approval, and lifetimes measured in seconds or minutes rather than days.
- **Confidence**: emerging (sound reasoning; no density or cost data attached)
- **Quote**: "An agent may wake up only when assigned a task, execute for a few seconds or minutes, and then become completely idle. Keeping a dedicated Pod alive for every potential agent quickly becomes wasteful."
- **Quote**: "An agent may pause while waiting for human approval before continuing."
- **Our assessment**: The "pause for human approval" case is the sharpest of the
  four for SRE purposes, because an approval-gated agent is idle for a
  *human-scale* duration (hours), not a machine-scale one — a Pod held open
  across an overnight approval is pure waste, and it is invisible as waste
  because the Pod looks healthy. The article gives no ratio (how many actors per
  worker, what the idle fraction actually is); the density figures come only
  from the project README (Claim 9), which is marketing-grade evidence.

### Claim 4: `agent-substrate` splits the agent lifecycle out of Kubernetes: Kubernetes manages Pods/Services/networking/storage/compute while `agent-substrate` manages "the lifecycle and placement of AI actors onto execution workers," and its abstractions deliberately mirror Kubernetes concepts
- **Evidence**: The architectural statement in the article, with the concrete
  analogy set (`WorkerPool`≈`NodePool`, `Worker`≈`Node`, `ActorTemplate`≈Pod
  spec) and the CRD manifests below it.
- **Confidence**: settled (checkable against the CRDs and the open-source repo)
- **Quote**: "Instead of treating every agent as a first-class Kubernetes workload, agent-substrate introduces an additional control plane above Kubernetes."
- **Quote**: "A WorkerPool is analogous to a NodePool, Workers are analogous to Nodes, and ActorTemplates correspond to the declarative specification of a Pod."
- **Our assessment**: Borrowing the Kubernetes vocabulary is a deliberate
  adoption strategy: an SRE who already reasons in `NodePool`/PodSpec can read
  `WorkerPool`/`ActorTemplate` without translation. The honest cost of that
  choice is a second, parallel mental model — `NodePool` describes *nodes*, so
  the "Worker ≈ Node" analogy invites exactly the confusion the article is
  trying to dissolve (it invites you to think of a Worker as a server, which is
  the one thing it is not). Worth flagging to readers.

### Claim 5: Workers and Actors are deliberately *not* Kubernetes custom resources — "Kubernetes only sees WorkerPools and ActorTemplates" — so the cluster runs a fixed number of execution Pods while the substrate manages a much larger number of logical agents
- **Evidence**: Stated explicitly, plus the `kubectl-ate get workers` /
  `get actors` transcripts (Claims 6, 7) as the demonstration: three Pod-backed
  workers, four suspended actors, no actor-to-Pod mapping for any of them.
- **Confidence**: settled (the transcripts show it)
- **Quote**: "The Worker or Actor is not represented as a custom resource in Kubernetes. Kubernetes only sees WorkerPools and ActorTemplates."
- **Quote**: "This separation allows the cluster to manage a fixed number of execution Pods while agent-substrate manages a much larger number of logical agents."
- **Our assessment**: This is the load-bearing decision of the whole design and
  it is also its biggest operational liability, which the article does not
  discuss: once Actors are invisible to Kubernetes, you lose the whole
  Kubernetes-native toolchain for them — `kubectl get`/`describe`/`logs -l`,
  `kubectl scale`, PDBs, NetworkPolicies keyed on agent identity, HPA on agent
  count, and RBAC on ServiceAccounts all stop applying to the entity you
  actually operate. The substrate re-implements a slice of this
  (`kubectl-ate logs actors`, per-actor egress policies, the ateapi state
  stream), but "a much larger number of logical agents" is precisely the
  population a platform team will first want to inspect during an incident. The
  guide should treat "what replaces the Kubernetes-native ops surface" as a
  required question for any team adopting a multiplexed-worker model, not an
  afterthought.

### Claim 6: An Actor is a logical entity scheduled onto a Worker when work arrives and removed when execution completes; Workers stay long-running Pods and Actors are the lightweight units that share them
- **Evidence**: The definition, plus the state vocabulary visible in the CLI
  transcript (`STATUS_SUSPENDED`, `VERSION`, no `ATEOM POD`/`ATEOM IP`).
- **Confidence**: settled
- **Quote**: "Instead, an Actor is a logical entity that can be scheduled onto an agent-substrate Worker when work arrives and removed when execution completes. Workers remain long-running Pods managed by Kubernetes, while Actors are lightweight execution units that share those workers."
- **Quote**: "In other words, Pods become the execution workers, not the deployment model for agents."
- **Our assessment**: "Removed when execution completes" is the part with real
  SRE consequences that the article leaves implicit — if an Actor is removed
  from a Worker at the end of a run, then everything that made the Pod-per-agent
  model attractive (identity, logs, network policy, audit trail) has to be
  re-created per run or reconstructed after the fact. The project README shows
  the suspension path preserves state via full-state snapshots, but the article
  does not distinguish "removed" (destroyed) from "suspended" (snapshot and
  parked), and the CLI transcript shows actors sitting at `STATUS_SUSPENDED`,
  which suggests suspension is the normal resting state, not removal. Treat the
  article's wording as imprecise here.

### Claim 7: The `ate.dev/v1alpha1` API surface is two CRDs — `WorkerPool` (a fixed set of execution workers, with a gVisor "ateom" image) and `ActorTemplate` (how an Actor executes, the analogue of a `PodTemplate`) — and both are namespaced Kubernetes objects with standard labels
- **Evidence**: Two complete CRD manifests reproduced in the article, both
  `apiVersion: ate.dev/v1alpha1`, both carrying the usual
  `app.kubernetes.io/*` / `kagent.dev/*` label vocabulary.
- **Confidence**: settled (verbatim manifests; the API group and kinds are
  checkable against the open-source repo)
- **Quote**: "Below is an example of a simple ActorTemplate in kagent. Note that it includes the `runsc` configuration, which serves as the execution entrypoint for gVisor."
- **Our assessment**: Worth noting for the guide that the default WorkerPool is
  three replicas of a gVisor-based worker image — a small number by design,
  because the density comes from multiplexing, not from a large worker fleet.
  Also note the author flags the manifest as abridged: "I omitted several
  kagent-specific fields, including the agent's name and additional
  configuration details", so the `containers[].command` and `env` blocks are
  elided with literal `...` in the source and are reproduced here as-is.

### Claim 8: The ActorTemplate pins both the workload image by digest and the sandbox runtime binary by per-architecture SHA256, and points snapshot storage at external object storage — three supply-chain and state-durability decisions in one object
- **Evidence**: Verbatim fields from the `ActorTemplate` manifest: a
  `@sha256:`-pinned agent image, a digest-pinned `pauseImage`, a `runsc` block
  with separate `amd64`/`arm64` `sha256Hash` + `url` (a gVisor *nightly* build
  URL), and `snapshotsConfig.location: gs://ate-snapshots/...`.
- **Confidence**: settled (the manifest is quoted; the practice is
  self-evidently deliberate)
- **Quote**: "Note that it includes the `runsc` configuration, which serves as the execution entrypoint for gVisor."
- **Our assessment**: Pinning the workload image by digest is routine good
  practice. Pinning the *sandbox runtime* by hash per architecture is not
  routine and is the more interesting decision: the thing enforcing isolation
  is versioned and integrity-checked like a dependency, not shipped as a
  mutable tag. The nightly gVisor URL in the example is the tension — a nightly
  URL pinned by hash is reproducible but means re-pinning whenever the base
  moves, which is a real operational chore. `snapshotsConfig.location` being
  mandatory and external is the third consequence: an Actor's durable state
  now lives in object storage, which puts snapshot restore on the critical path
  for every wake-up and makes the bucket a new backup/RPO concern.

### Claim 9: The project README claims 10x higher density than standard container runtimes, sub-500ms resume at over 500 suspend/resume activations per second, and a demo multiplexing ~250 stateful actors across 8 physical pods at 30x+ oversubscription
- **Evidence**: The substrate README's opening paragraph and demo section.
  Density is a relative claim ("than standard container runtimes") with no
  stated baseline, node shape, or per-actor memory footprint; the 250-actors-
  on-8-pods figure comes from a demo video description. State preservation
  across hibernation is claimed via "full-state snapshots."
- **Confidence**: anecdotal (vendor self-reported, no methodology, no
  independent reproduction)
- **Quote**: "engineered to run millions of sandboxes with 10x higher density than standard container runtimes"
- **Quote**: "sub-500ms resume operations at over 500 suspend/resume activations per second with native zero-trust kernel and network isolation"
- **Quote**: "Watch the Agent Substrate cluster multiplex ~250 stateful actors across just 8 physical pods."
- **Our assessment**: These are the only numbers anywhere in this source and
  they should not be repeated in the guide as results. Note the three figures
  are not commensurable and may not describe the same configuration: 10x density
  is relative to an unnamed baseline, 250/8 is ~31x and comes from a demo, and
  "500 suspend/resume activations per second" is a control-plane activation rate
  (not necessarily agent completions). The 30x+ oversubscription claim and the
  ~250-on-8 demo are consistent with each other but with the same demo setup.
  What the numbers *do* establish is the order of magnitude: multiplexed-worker
  agent hosting is presented as 1–2 orders of magnitude denser than
  Pod-per-agent, which is the claim the design needs to be worth its complexity.

### Claim 10: Worker capacity is versioned through a node label, and an unlabeled node silently hosts no workers — a version-skew failure mode specific to a substrate that owns its own dataplane
- **Evidence**: The README's "Worker capacity is versioned" paragraph and the
  documented remediation command. `kubectl get ds -n ate-system -l app=atelet
  -L ate.dev/substrate-version` is given as the diagnostic.
- **Confidence**: settled (documented, with the exact label and the exact fix)
- **Quote**: "Worker capacity is versioned: the dataplane (the atelet DaemonSet and the worker pods) schedules only on nodes that carry the `ate.dev/substrate-version` label"
- **Quote**: "A node added later hosts no workers until you label it with the installed version"
- **Our assessment**: This is the single most operationally useful sentence in
  the linked README, and it is not in the article. Any layer that puts its own
  agent-side dataplane on the node introduces a version-skew dimension that
  `kubectl` will not warn you about: the node is `Ready`, the DaemonSet pod is
  running, and there are simply no Workers there — which, under multiplexing,
  means reduced capacity for the *whole pool* rather than a visibly broken
  Pod. On GKE the README notes autoscaling, auto-repair, and node upgrades all
  add nodes, so the skew is created by normal cluster lifecycle, not by
  operator error. Corroborates the corpus's general pattern of
  version-skew-as-incident-cause (`docs-litellm-version-support.md` territory)
  at a new layer.

### Claim 11: The article's central observability requirement — "observability must follow the logical agent, not the underlying Pod" — is implemented as a reserved `ate.*` identity metadata namespace on logs, with actor identity deliberately barred from metric labels
- **Evidence**: `docs/observability.md`. Six `ate.*` keys
  (`ate.actor.name`, `ate.atespace`, `ate.actor.uid`, `ate.template.name`,
  `ate.template.atespace`, `ate.actor.container.name`) are injected into wrapped
  container stdout. The metrics side states the cardinality rule explicitly:
  high-cardinality actor identity is kept off metrics and carried on logs and
  traces instead, with per-actor usage shipped as a log event rather than a
  metric.
- **Confidence**: settled (documented design with named keys)
- **Quote**: "When an Actor executes on different Workers over its lifetime, observability must follow the logical agent, not the underlying Pod."
- **Quote**: "Logs, traces, audit records, and execution history should all be associated with the Actor regardless of where it was scheduled."
- **Quote**: "High-cardinality actor identity (name/uid/atespace) stays off metrics entirely and lives on logs and traces instead — for resource usage, on the per-actor usage events."
- **Our assessment**: The `ate.actor.uid` — server-assigned, "unique to the
  lifetime of an actor" — is the substrate's answer to the article's identity
  question, and it is the right primitive: a per-lifetime UID that survives
  worker migration and template versioning. The cardinality rule is the more
  interesting half and is a genuinely reusable lesson: once your deployment
  unit is multiplexed, per-agent resource usage is inherently high-cardinality,
  and the standard move is to move it onto the log/event channel where
  cardinality is free rather than letting an agent name become a metric label.
  Do **not** read this as "observability is solved." See Claim 12.

### Claim 12: The same docs show three concrete ways actor attribution is *not* solved: platform logs cannot carry trace context for an actor's own output, actor identity cannot be sampled out of the lifecycle stream without creating silent wrongness, and the collector labels an actor's spans with the egress gateway's Pod name
- **Evidence**: All three from `docs/observability.md`, with issue numbers for
  the two that are known-incomplete.
  (a) Actor-emitted log lines carry trace context only if the actor emits it
  itself — the forwarder "cannot tell which request produced a given line"
  (tracked as #853).
  (b) The lifecycle stream ("Actor state changed", "Actor crashed") is read as
  last-write-wins per actor uid, so dropping any record silently reports a stale
  state; the docs call sampling it "a correctness bug rather than a cost trade."
  (c) Actor SDK telemetry is routed through the egress gateway, so a collector
  enriching by source IP (`k8sattributes`) attaches the *gateway's*
  `k8s.pod.name` and `k8s.deployment.name=atenet-egress` to the actor's spans
  and metrics (identity injection tracked as #853 / #761).
- **Confidence**: settled (documented, self-reported gaps)
- **Quote**: "Substrate cannot supply them: one forwarder goroutine covers a container's whole output stream and cannot tell which request produced a given line."
- **Quote**: "Never sample or filter the lifecycle stream. A consumer takes the last event for an actor's uid, so one dropped record reports a stale state with no sign that anything is missing. This is the one stream where a sampling policy is a correctness bug rather than a cost trade."
- **Quote**: "The collector sees the gateway, not the actor."
- **Our assessment**: This is the finding that should change guide advice. The
  article's observability section is aspirational; the project's own docs show
  that identity-preserving observability across a multiplexed worker pool is an
  *open engineering problem*, not a solved one — and (c) is a silent wrong-Pod
  attribution bug, the exact failure mode an operator would blame on the agent.
  Note also the traces are head-sampled at 1% at the router, so a per-actor
  wake-up distribution has to be answered from the unsampled log record, not
  the histogram. For the guide: any recommendation to multiplex agents onto
  shared workers must be paired with "you will need to build or buy actor-scoped
  correlation yourself, and verify which Pod your backend actually attributed
  the span to."

### Claim 13: Actor identity is namespaced twice — by `(atespace, name)` and by server-assigned `uid` — and actor names are only unique within an atespace
- **Evidence**: `docs/observability.md` and the CLI: `--atespace` is a required
  flag because "actor names are only unique within an atespace"; every identity
  key set carries both `ate.actor.name` and `ate.atespace`, plus the uid.
- **Confidence**: settled
- **Quote**: "actor names are only unique within an atespace, so an actor is always addressed by `(atespace, name)`."
- **Our assessment**: "Atespace" is the substrate's tenant/ownership boundary,
  and the name is the *template*-derived logical agent while the uid is the live
  instance. That three-level identity (template → named actor → per-lifetime
  uid) is a cleaner answer to "who is this agent" than a Kubernetes
  ServiceAccount is, because ServiceAccount identity is minted per deployment
  and says nothing about which logical agent or which version is running. The
  naming, however, is a usability trap inherited from Kubernetes CRDs:
  `ate.atespace` and `ate.namespace` are different things, and an operator who
  greps for `namespace` will silently get nothing.

### Claim 14: The `ate.*` metadata namespace is spoofing-resistant by construction — any key in that namespace emitted by the workload itself is dropped before the record is written
- **Evidence**: `docs/observability.md`, stated as an explicit design rule rather
  than a limitation.
- **Confidence**: settled
- **Quote**: "`ate.*` is reserved for Substrate. An actor's own log lines pass through untouched except for keys in that namespace, which are dropped before the record is written, so nothing a workload emits can be read as platform-issued attribution."
- **Our assessment**: A small, high-value security pattern for Ch06: when a
  platform injects trusted identity metadata into untrusted workloads' output,
  it must own the namespace *and* strip workload-supplied keys from it.
  Otherwise a compromised or merely confused agent writes
  `ate.actor.uid: <someone-else>` into its own log line and every downstream
  audit query — and every per-agent cost rollup — attributes its traffic to
  another agent. This is the log-injection sibling of the host-bound credential
  pinning pattern in `blog-litellm-lap-internal-agent-30-percent.md` Claim 5:
  shift the trust basis from the value to the channel.

### Claim 15: Worker-pool saturation is answered with bounded request parking — the router retries the resume with backoff up to a 5s budget and returns a capacity 503 only then — plus a fixed-capacity admission lot and per-actor request de-duplication
- **Evidence**: `docs/request-parking.md`. `ResourceExhausted`,
  `FailedPrecondition`, and `Unavailable` from `ResumeActor` are retryable;
  `NotFound` → `404`, `DeadlineExceeded` → `504`,
  `PermissionDenied`/`Unauthenticated` → `403`/`401` fail fast. Flags:
  `--parked-request-budget` (5s), `--parked-request-max` (1024),
  `--parked-request-retry-interval` (100ms), `--parked-request-retry-factor`
  (1.1), `--parked-request-retry-jitter` (0.1). Observed via
  `atenet.router.parking.active`, `atenet.router.parking.wait.duration`
  (`outcome` ∈ served / budget_exhausted / canceled / timeout / error), and
  `atenet.router.parking.rejected`.
- **Confidence**: settled (documented behavior, defaults, and instruments)
- **Quote**: "Failing fast turns a sub-second blip into a user-visible error."
- **Quote**: "retrying the resume until the actor becomes routable or a bounded wait elapses — instead of immediately returning `503` to the client"
- **Quote**: "they share a single in-flight `ResumeActor` call and all park on its result, so a hot actor consumes N parking slots but only one control-plane RPC."
- **Our assessment**: This is the single most SRE-relevant mechanism in the
  whole source set, and it is absent from the article. Oversubscription is the
  entire premise of the design, so saturation is the *normal* steady state, not
  an incident — and a naive router that maps `no free workers` to `503` would
  manufacture user-visible errors out of expected behavior. Three details are
  worth stealing regardless of substrate: (1) a bounded park budget with an
  explicit fail-closed outcome, so waiting is capped and visible;
  (2) the admission lot with a distinct shed metric, so overload is bounded and
  counted; (3) the per-actor flight registry, so a hot actor cannot stampede the
  control plane — the same class of fix as the concurrent-resume `Aborted` retry
  and the same lesson as PagerDuty's priority queue for user input over
  sub-agent results (`blog-pagerduty-sre-agent-architecture.md` Claim 10).
  The `budget_exhausted` outcome is also the right signal for the guide to name:
  "capacity, not a fault, is the bottleneck."

### Claim 16: Actor egress is default-deny and per-actor, and telemetry export is subject to it — so an actor that wants to ship its own traces must be granted an explicit `http` rule, and the failure mode is a silent `connection reset by peer` plus a 45s–2min reconnect delay
- **Evidence**: `docs/observability.md` ("Actor telemetry needs an egress
  policy"), the two example `EgressPolicy` manifests (collector Service +
  ports 4317/4318, `http` not `https` because OTLP/gRPC is h2c), plus the
  README's egress credential injection defaulting to an "empty, default-deny"
  namespace policy that must be granted per-atespace.
- **Confidence**: settled (documented with manifests and the exact error
  strings)
- **Quote**: "An actor with no policy, or a policy with no matching rule, cannot reach the collector at all. The SDK sees `Unavailable: connection reset by peer` on each export, and the gateway logs `egress denied: actor has no egress policy`."
- **Quote**: "Expect the first successful export 45s to two minutes after the policy appears."
- **Our assessment**: Default-deny egress per logical agent is exactly the
  control the article asks for under "Security and Policy" ("expressed at the
  ActorTemplate level and selectively overridden for individual Actors" — the
  docs note a template-level default policy is still an open proposal, #1558,
  so today it is per-actor only). Two traps: the rule must be `http` and not
  `https` or OTLP export fails in a way that looks like a collector problem,
  and applying the policy to a *running* actor costs up to two minutes because
  the SDK is in gRPC reconnect backoff and the gateway caches the miss for 10s.
  Note also the honest self-criticism in the docs: a default-deny egress policy
  means your own observability stack is not reachable by default, which is a
  real operational cost of "secure by default" that belongs in any guide
  treatment of this pattern.

### Claim 17: Actor state is a real state machine with committed transitions, and each transition emits a record that is authoritative by resource rather than by message
- **Evidence**: `docs/observability.md`. `ate.actor.state` takes lowercased
  `ateapipb.ActorState` values "so the log vocabulary and the state machine
  cannot fork"; a create counts as a change (`ate.actor.operation.name: create`)
  because "an actor that is created and never resumed would have no record at
  all, no matter how long you keep your logs"; records are emitted *after* the
  store commit and every commit is version-checked, so a losing writer writes
  nothing. The docs state the limits of the stream explicitly: it only writes on
  change, records can be lost like any log, and "a gap looks the same as an
  actor that just sat still."
- **Confidence**: settled
- **Quote**: "The record goes out after the store commit, never before, and the state is read straight off the committed record rather than named by the caller."
- **Quote**: "Records can also go missing, like any other log, and a gap looks the same as an actor that just sat still."
- **Our assessment**: Two details generalize well beyond this project. First,
  the operation/state split — `suspended` is reachable from a suspend and
  `paused` from a pause, and the two differ in whether the worker was released —
  is a good reminder that a state name alone does not tell you the resource
  consequence; log the transition that caused the state. Second, the honest
  "what this stream won't tell you" section is a model for source notes and
  guide text alike: a derived-state log that is authoritative about *how* and
  *when* but silent about *now* must be paired with an explicit instruction to
  query the control plane for current state. Treating that log gap as "the
  agent is idle" would be a real incident-diagnosis trap.

### Claim 18: The article's four open questions are identity ownership, policy attachment point, ownership/quotas/billing across tenants, and observability — and the article is explicit that these are questions, not answers
- **Evidence**: The "Challenging More Than Deployment Model" section poses each
  as a question and offers a pointer (Christian Posta's post on identity,
  `agentgateway` for mediation) rather than a position. Ownership is posed
  twice with no proposal at all.
- **Confidence**: settled (the article is unambiguous that these are open)
- **Quote**: "Should an agent’s identity really be tied to a Pod or its Service?"
- **Quote**: "Should access control, network policy, and runtime permissions instead be expressed at the ActorTemplate level and selectively overridden for individual Actors?"
- **Quote**: "How are quotas, billing, and lifecycle managed across teams and tenants when AI agent execution is no longer tied one-to-one with Pods?"
- **Our assessment**: The article's real contribution is the question list, and
  it is a better one than its conclusion. Quota and billing across tenants is the
  question with the largest operational blast radius and the least progress
  visible in the linked docs: `ate.atespace` gives you a tenant boundary to bill
  against, but the article never says how a team is charged for actors that
  share a worker, and cost attribution per logical agent is exactly what the
  observability doc says cannot live on metrics. For the guide: this is the gap
  to name — the multiplexed-worker model has an unresolved cost-attribution
  story, and "cheaper per agent" (Claim 9) is not the same as "chargeable per
  agent."

### Claim 19: `agent-substrate` is pre-1.0 with no backward-compatibility guarantee, and supports only the latest stable Kubernetes release plus the previous minor
- **Evidence**: README "Status and compatibility" section, plus the component
  tour listing `ateom-gvisor` (in-Pod `runsc` checkpoint/restore helper) and
  `ateom-microvm` (cloud-hypervisor peer), `atelet` (node DaemonSet supervising
  worker Pods), `atecontroller`, `atenet`, and a `podcertcontroller` that
  "provides Pod Certificate signers that will eventually ship in upstream
  Kubernetes."
- **Confidence**: settled
- **Quote**: "Agent Substrate is pre-1.0. We are not making any guarantees about backward compatibility at this stage, and APIs and behavior may still change significantly."
- **Quote**: "Currently we aim to support the latest stable release of Kubernetes, and the previous minor release."
- **Our assessment**: Relevant to any guide recommendation to adopt this
  pattern: the CRDs in the article are `v1alpha1` from a pre-1.0 project with an
  explicit no-stability guarantee. The honest reading is that the *pattern* is
  the transferable contribution and the *implementation* is not yet something to
  standard-build on. The two-arithmetic constraint (latest stable + previous
  minor) also means an N-2 Kubernetes cluster — still common in enterprises —
  is out of scope, which matters for platform teams who cannot upgrade on the
  substrate's schedule.

### Claim 20: The project positions itself as framework-agnostic and explicitly not an agent SDK, and its credential-injection design starts from an empty default-deny policy
- **Evidence**: README "Framework Agnostic & Compatibility" (agents, LangChain,
  Claude Code / Codex / Antigravity, MCP servers as Actors) and the quickstart's
  `{"name":"k8s.io"}` credential provider with an empty default-deny namespace
  policy. `agentgateway` (the mediation layer the article proposes) is a Solo.io
  project that has joined the Agentic AI Foundation and handles MCP, A2A, and
  LLM traffic in one data plane with per-hop policy and audit.
- **Confidence**: settled
- **Quote**: "It is not an SDK for building agents, but rather a system for running them at scale."
- **Quote**: "Agent Substrate is intended to be a low-opinion system."
- **Our assessment**: The layer separation is the right one and worth stating
  plainly for the guide: substrate runs actors, the harness/framework builds
  agents, and a gateway mediates their traffic. The default-deny credential
  posture is the pattern (`blog-litellm-lap-internal-agent-30-percent.md`
  Claim 5 host-bound pinning is the complementary mechanism — default-deny
  namespace policy decides *which* secrets an atespace may read; pinning decides
  *where* a given credential may be sent). Worth flagging that "framework
  agnostic" is asserted and plausible (it manages OCI containers at the kernel
  level via gVisor) but not independently verified here.

## Concrete Artifacts

### `WorkerPool` CRD — verbatim from the article

```yaml
apiVersion: ate.dev/v1alpha1
kind: WorkerPool
metadata:
  labels:
    app.kubernetes.io/instance: kagent
    app.kubernetes.io/name: kagent
  name: kagent-default
  namespace: kagent
spec:
  ateomImage: ghcr.io/kagent-dev/substrate/ateom-gvisor:v0.0.6
  replicas: 3
```

### `ActorTemplate` CRD — verbatim from the article (author notes several kagent-specific fields were omitted)

```yaml
apiVersion: ate.dev/v1alpha1
kind: ActorTemplate
metadata:
  labels:
    app.kubernetes.io/managed-by: kagent
    kagent.dev/sandbox-agent: hello-substrate
  name: hello-substrate
  namespace: kagent
spec:
  containers:
  - command:
    - /app
    ...
    env:
    ...
    image: cr.kagent.dev/kagent-dev/kagent/golang-adk@sha256:e01479b52280b0eae9e2808cc68392ba98fd737782496ff256847257e6bb8ed1
    name: kagent
  pauseImage: gcr.io/gke-release/pause@sha256:bcbd57ba5653580ec647b16d8163cdd1112df3609129b01f912a8032e48265da
  runsc:
    amd64:
      sha256Hash: efd12935f6654c91a1389710eb8dfa4d12b6b9be00db87526dc2eb584ad00119
      url: gs://gvisor/releases/nightly/2026-06-02/x86_64/runsc
    arm64:
      ...
  snapshotsConfig:
    location: gs://ate-snapshots/kagent/hello-substrate
  workerPoolRef:
    name: kagent-default
    namespace: kagent
```

### `kubectl-ate get workers` / `get actors` — verbatim from the article

```
$ kubectl-ate get workers
NAMESPACE   POOL             POD                                         STATUS   ASSIGNED ACTOR
kagent      kagent-default   kagent-default-deployment-ddfcfbdd7-54pb7   FREE     <none>
kagent      kagent-default   kagent-default-deployment-ddfcfbdd7-jmjl5   FREE     <none>
kagent      kagent-default   kagent-default-deployment-ddfcfbdd7-z2mmh   FREE     <none>

$ kubectl-ate get actors
NAMESPACE   TEMPLATE                  ID                                                                STATUS             ATEOM POD   ATEOM IP   VERSION
kagent      hello-substrate           a786a0c4-c2c8-44e5-9ea5-67b64f41deb1                              STATUS_SUSPENDED   <none>                 5
kagent      hello-substrate           asr-kagent-hello-substrate-019efbb5-cc48-7601-8fc6-985e6239aa05   STATUS_SUSPENDED   <none>                 5
kagent      hello-substrate-linsun    0c82223d-cc14-40c8-a25c-5ee00fe153ae                              STATUS_SUSPENDED   <none>                 5
kagent      hello-substrate-linsun3   asr-ce96fc0ee592bf1e12336461                                      STATUS_SUSPENDED   <none>                 5
```

> Read this as the article's core evidence: three `FREE` Workers, four
> `STATUS_SUSPENDED` Actors at `VERSION` 5, and **no actor mapped to any Pod** —
> the fixed-pool-fronting-many-logical-agents claim, shown rather than asserted.

### Actor identity keys — verbatim from the substrate `docs/observability.md`

```
* `ate.actor.name`: The name of the actor (e.g., `my-counter-1` or `test`).
* `ate.atespace`: The atespace the actor lives in (e.g., `ate-demo-counter`).
* `ate.actor.uid`: Server-assigned UID of the actor, unique to the lifetime of an actor.
* `ate.template.name`: The name of the actor's ActorTemplate (e.g., `counter`).
* `ate.template.atespace`: The atespace of the actor's ActorTemplate (e.g., `ate-demo-counter`).
* `ate.actor.container.name`: The name of the container within the actor that produced the log line
  (e.g., `counter`), so a multi-container actor's logs can be demultiplexed by container.
```

### Log query dimensions — verbatim from the substrate `docs/observability.md`

```
labels."ate.actor.name"="test"          # actor-centric, across migrations and suspend/resume
labels."ate.atespace"="ate-demo-counter" # all instances in a tenant
labels."ate.template.name"="counter"     # all instances created from one template
resource.labels.pod_name="counter-c995fdf4c-m7d96"  # all actors multiplexed onto one worker Pod
```

### Actor state-transition log record — verbatim from the substrate `docs/observability.md`

```json
{"time":"…","level":"INFO","msg":"Actor state changed",
 "ate.atespace":"ate-demo-counter","ate.actor.name":"counter-1","ate.actor.uid":"8f2a…",
 "ate.template.atespace":"ate-demo-counter","ate.template.name":"counter",
 "ate.actor.operation.name":"suspend","ate.actor.state":"suspended",
 "trace_id":"4bf92f…","span_id":"00f067…","trace_flags":"01"}
```

### Actor egress policy to allow OTLP export — verbatim from the substrate `docs/observability.md`

```bash
# Kind
kubectl ate create egress-policy <actor-name> -a <atespace> -f - <<'EOF'
rules:
- http:
    hostnames: ["opentelemetry-collector.otel-system.svc"]
    ports:
      numbers: [4317, 4318]
EOF

# GKE, with the managed OpenTelemetry collector
kubectl ate create egress-policy <actor-name> -a <atespace> -f - <<'EOF'
rules:
- http:
    hostnames: ["opentelemetry-collector.gke-managed-otel.svc.cluster.local"]
    ports:
      numbers: [4317, 4318]
EOF
```

> The `http` (not `https`) requirement is load-bearing: the OTLP/gRPC exporter
> is gRPC over cleartext HTTP/2 (h2c) on 4317.

### Request-parking flags and defaults — verbatim from the substrate `docs/request-parking.md`

| Flag | Default | Meaning |
|---|---|---|
| `--parked-request-budget` | `5s` | Park budget per resume *flight* |
| `--parked-request-max` | `1024` | Max concurrent parked requests; beyond it, shed (503). `0` disables |
| `--parked-request-retry-interval` | `100ms` | Delay before a parked request's first resume retry |
| `--parked-request-retry-factor` | `1.1` | Retry-delay multiplier (>= 1) |
| `--parked-request-retry-jitter` | `0.1` | Random fraction added per retry to de-synchronize parked requests |

### Retryability table — verbatim from the substrate `docs/request-parking.md`

```
OK                                   Route to worker
Aborted (concurrent resume)          Retry (always)
ResourceExhausted (no free worker)   Park & retry (when enabled)
FailedPrecondition (transient state) Park & retry (when enabled)
Unavailable (control-plane blip)     Park & retry (when enabled)
NotFound                             Fail fast -> 404
DeadlineExceeded                     Fail fast -> 504
PermissionDenied / Unauthenticated   Fail fast -> 403 / 401
```

### Worker-capacity version skew — verbatim from the substrate README

```
Worker capacity is versioned: the dataplane (the atelet DaemonSet and the worker
pods) schedules only on nodes that carry the `ate.dev/substrate-version` label...

kubectl label node <node> ate.dev/substrate-version=<build version>
kubectl get ds -n ate-system -l app=atelet -L ate.dev/substrate-version
```

### Agent-scoped CLI error when the actor is not resident — verbatim from the substrate `docs/observability.md`

```
$ kubectl ate logs actors test -a demo
Error: actor test is not currently running on any worker pod
```

> This is the concrete replacement for `kubectl logs <pod>` in a multiplexed
> world, and its failure mode is the point: the default `kubectl ate logs`
> queries only the worker Pod the actor is *currently* on, so historical logs
> across past workers require a centralized backend.

## Cross-References

- **Corroborates**:
  - `blog-litellm-lap-internal-agent-30-percent.md` (Claim 1 — separating a
    persistent "brain" pod from ephemeral per-session sandboxes reduces latency,
    raises success rate, lowers cost). This is the closest architectural
    neighbor in the corpus and it independently arrived at the same topology:
    a small fixed pool of long-lived Pods fronting many short-lived execution
    units. LiteLLM's version is a per-session E2B sandbox pool under a shared
    harness Pod; this source's is a fixed `WorkerPool` of gVisor workers under
    a substrate control plane. Two independent teams, same shape, different
    motivation (LiteLLM: cold-start latency on Slack Q&A; Solo.io: density for
    idle agents).
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 12 — IO-bound agentic
    workloads do not benefit from service boundaries; splitting them across
    services "buys deployment, service discovery, network failure modes,
    distributed tracing — without buying the thing services are for"). Same
    conclusion as this source's headline ("Pods become the execution workers,
    not the deployment model for agents") argued from an application-architecture
    angle instead of a scheduler angle. Note the qualifier PagerDuty's claim
    carries and this one does not: both are about IO-bound agents.
  - `blog-pagerduty-sre-agent-architecture.md` (Claim 14 — co-locating agents
    collapses the transport layer from broker/durable-store to an in-process
    `asyncio.Queue`; and its note that "multiple concurrent investigation runs
    can still land on different pods"). Confirms that treating the Pod as an
    execution substrate while the agent is a logical entity is the direction
    practitioners are already moving, arrived at from a different problem.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` (Claim 3 — the default
    guardrail is to deny agents any world-mutating action, writes run in a
    sandbox, and anything that breaks the sandbox needs an additional check).
    Google's production guardrail and this source's per-actor gVisor sandbox
    (`runsc` as the execution entrypoint, `ateom-gvisor` as the in-Pod
    checkpoint/restore helper) are the same control at different layers:
    policy decides what the agent may do, the sandbox contains what it does do.

- **Contradicts**: None, and no contradiction issue filed. Two tensions were
  examined and both resolved as conditioning variables rather than
  disagreements:
  1. *Pod-based attribution vs. protocol-based attribution.* This article lists
     "Observability systems can attribute logs, metrics, and traces to
     individual agents" as a benefit of Pod-per-agent (Claim 2), while
     `docs-litellm-a2a-agent-gateway.md` Claim 2 records that agent-level trace
     grouping and spend attribution are a manual header-forwarding obligation
     that fails silently, and `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
     Claim 4 records that agent identity attributes must be hand-authored
     because "Auto-instrumentation can't infer your conversation boundaries or
     your agent identity." These are different mechanisms (Kubernetes resource
     identity vs. application-level header/attribute propagation), so the guide
     can carry both: the Pod supplies a resource identity, and something else
     still has to supply the correlation and attribution. Not a contradiction —
     the article's own Observability section (Claim 11) concedes the point.
  2. *"Pods are excellent execution environments" vs. per-agent Pods being
     wasteful.* The article is deliberately contrasting two eras (Pod-per-agent
     solved five problems, then broke density; the substrate keeps the Pod as
     the execution unit and moves the other three roles above it), not
     recommending two incompatible things.

- **Extends**:
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` (Claim 2 — three
    attributes are mandatory for agent tracing: `gen_ai.conversation.id`,
    `gen_ai.agent.name`, `gen_ai.operation.name`; Claim 6 — multi-agent systems
    need distinct agent names per sub-agent and explicit handoff spans). This
    source supplies the infrastructure-side half of that contract: the substrate
    defines its own reserved identity namespace (`ate.actor.uid` as the
    per-lifetime grouping key, `ate.actor.name` as the swim lane) and its own
    docs confirm actor identity cannot be inferred at the platform layer — it
    must be injected, and it cannot go on metrics. The pairing of the two notes
    is what a guide chapter needs: the *application* must stamp identity on its
    spans, and the *platform* must preserve and route that identity across
    worker migrations.
  - `docs-litellm-a2a-agent-gateway.md` (Claim 2 — trace grouping and per-agent
    spend attribution are a forwarding obligation, not a guarantee; Claim 3 —
    the caller's virtual key and end-user ID are not propagated, and identity
    re-propagation is manual). The same failure class one layer up: once the
    deployment unit stops being the agent, agent identity must be threaded
    explicitly at every hop. The gateway note documents the A2A-protocol
    manifestation (headers); this note documents the substrate manifestation
    (`ate.*` metadata, and the gap where the collector attributes an actor's
    span to the egress gateway's Pod).
  - `docs-litellm-a2a-agent-permissions.md` (Claim 1 — A2A agent permission
    resolution is two-level (Key, Team) with a **fail-open** default when
    neither sets restrictions). Useful contrast for the identity/policy section:
    the article's substrate design defaults egress to **deny**
    (`docs/observability.md`: "An actor with no policy ... cannot reach the
    collector at all"; README: bundled credential provider starts "with an
    empty, default-deny" namespace policy). Two agent-governance stacks in the
    corpus with opposite defaults — a guide recommendation on per-agent policy
    should name the default explicitly rather than saying "add authorization".
  - `docs-google-sre-prodcast-04-10-platform-engineering.md` (Claim 4 — day-two
    concerns such as observability, cost controls, and security/compliance
    visibility should be surfaced *up* to application teams by the platform so
    they get them "for free"; Claim 7 — deployment archetypes are reusable
    deployment patterns with reliability characteristics built in; Claim 8 —
    archetypes apply failure-domain understanding and the platform exposes the
    choice as a simple dropdown). The substrate is a deployment archetype for
    agents, in the exact sense of that episode: a platform team builds the
    multiplexing, sandboxing, and egress story once and hands teams a template.
    Claim 15 (request parking) and Claim 16 (default-deny egress) are exactly
    the "day-two shifted down" work — and, read against Claim 9 of the same
    note, a place where the "free" is a cost the platform team has to be honest
    about, since cheaper-per-agent is not chargeable-per-agent (Claim 18).
  - `blog-litellm-google-ai-studio-managed-agents.md` (Claim 2 — LiteLLM is
    "just the auth + routing layer" and does not persist agents, so the agent
    lives on Google's side; Claim 7 — deleting an agent via Google's API
    directly creates a cache inconsistency the proxy cannot reconcile). The
    same architectural split — a control plane that owns agent lifecycle while
    something else owns execution — at the SaaS layer instead of the Kubernetes
    layer, and with a concrete failure mode this source does *not* yet have:
    the LiteLLM note's out-of-band deletion is the substrate's
    `kubectl ate` vs. Google-console equivalent, and the article's own
    multi-tenancy question (Claim 18) is where that failure would live.
  - `blog-promptfoo-indirect-prompt-injection-web-agents.md` (Claim 11 — the
    "lethal trifecta" of private data access + untrusted content + external
    communication defines the risk envelope). Per-actor default-deny egress
    (Claim 16) and per-actor gVisor isolation are a structural mitigation axis
    for that trifecta: they constrain the *external communication* leg and the
    blast radius of the private-data leg. Note the limit the promptfoo note
    implies and this source does not address — a sandboxed actor with egress
    granted to exactly the hosts it needs can still assemble all three legs,
    so sandboxing bounds impact rather than preventing the trifecta.
  - `failure-litellm-prisma-reconnect-event-loop-blocking.md` — not cited by
    claim, but the closest corpus precedent for the failure class this design
    introduces: an agent runtime whose blocking behavior is invisible from the
    outside because the entity being debugged (an Actor) is not the entity the
    monitoring stack watches (a Pod). Worth the Smith pairing when Ch07 covers
    multiplexed-worker failure diagnosis.

- **Novel** — first coverage in the corpus of:
  - **The deployment/identity/lifecycle-unit question for AI agents at the
    Kubernetes layer.** Nothing in the corpus previously asked whether the Pod
    is the right unit for an agent, let alone proposed an alternative.
  - **`agent-substrate`'s API vocabulary**: `ate.dev/v1alpha1`, `WorkerPool`,
    `ActorTemplate`, `Worker`, `Actor`, `atespace`, `ateom`, `atelet`, and the
    `kubectl-ate` CLI — with complete CRD manifests and CLI transcripts.
  - **A multiplexed worker pool as the agent hosting model**, with a
    complementary `Worker`≈`Node` / `WorkerPool`≈`NodePool` /
    `ActorTemplate`≈PodSpec analogy set.
  - **Per-lifetime actor UID as the correlation key that survives worker
    migration**, and the three-level identity (template → named actor → uid).
  - **A cardinality firewall for agent observability**: high-cardinality actor
    identity kept off metric labels entirely and carried on logs/traces, with
    per-actor usage shipped as a log event.
  - **Anti-spoofing reserved metadata namespaces** — platform-injected identity
    keys are dropped if the workload emits them, so no agent can forge its own
    attribution.
  - **Request parking** — bounded park budget + fixed admission lot + per-actor
    flight de-duplication as the designed response to *expected* worker-pool
    saturation, with a `budget_exhausted` outcome that distinguishes capacity
    from fault.
  - **Default-deny, per-actor egress policy that also governs telemetry export**,
    including the `http`-not-`https` rule for OTLP and the 45s–2min reconnect
    penalty.
  - **Worker-capacity version skew via node label** (`ate.dev/substrate-version`)
    as a silent capacity-loss failure mode on autoscaled clusters.
  - **The concrete attribution gaps**: platform logs cannot supply trace context
    for actor-emitted lines; sampling the lifecycle stream is "a correctness bug
    rather than a cost trade"; and a source-IP-enriching collector labels an
    actor's spans with the egress gateway's Pod (`k8s.deployment.name=atenet-egress`).
  - **Per-actor sandbox binaries pinned by per-architecture SHA256** (gVisor
    `runsc`) with snapshots in external object storage.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add an explicit decision procedure for
  agent hosting topology, replacing the current implicit "one Pod per agent."
  The rule this source supports: **Pod-per-agent is correct for long-lived,
  continuously-available agents and must remain the default**, because
  isolation, ServiceAccount identity, unchanged network/admission policy,
  per-agent log/metric/trace attribution, and Kubernetes-native scheduling all
  come free (Claim 2). Switch to a multiplexed worker pool only when the agent
  population is **mostly idle** — bursty, task-triggered, or human-approval-gated
  — because that is the only condition under which a dedicated Pod per *potential*
  agent is waste rather than headroom (Claim 3). Pair with the
  `blog-litellm-lap-internal-agent-30-percent.md` brain/sandbox split as the
  existing corpus precedent for the same topology from a different motivation,
  and with `blog-pagerduty-sre-agent-architecture.md` Claim 12 for the
  application-layer version of the argument.

- **Chapter 05 (LLM Ops Reliability)**: Three additions.
  (1) **Oversubscription makes saturation the normal steady state, so capacity
  errors need a designed response, not a fail-fast router.** Add request
  parking (Claim 15) as the pattern: a bounded park budget with an explicit
  fail-closed outcome, a fixed admission lot with its own shed counter, and
  per-entity request de-duplication so a hot agent cannot stampede the control
  plane. Name `budget_exhausted` as the signal that separates "capacity is the
  bottleneck" from "something is broken."
  (2) **Add actor-scoped state as a first-class signal.** State transitions are
  committed, post-commit, version-checked, and readable last-write-wins per
  identity (Claim 17) — and the guide must carry the companion warning that
  this stream only writes on change and can have gaps, so current state comes
  from the control plane and this stream answers *how* and *when*, not *now*.
  (3) **Version skew as a capacity incident.** If a platform layer runs its own
  node-level dataplane, worker capacity becomes label-gated and a `Ready` node
  with an unlabeled dataplane contributes nothing (Claim 10) — on autoscaled
  clusters this is created by normal node lifecycle, not operator error.
  Also carry the explicit non-claim: this source's density and latency figures
  (Claim 9) are vendor self-reported with no methodology and should not be
  reproduced as results.

- **Chapter 02 (Observability)**: Add the cardinality rule as a first-class
  lesson (Claim 11): once the deployment unit is multiplexed, per-agent
  resource usage is inherently high-cardinality, so actor identity must be kept
  **off metric labels** and carried on logs and traces, with per-actor usage
  emitted as a log event. Add the reserved-namespace anti-spoofing pattern
  (Claim 14) as the required rule for any platform that injects trusted
  identity metadata into untrusted workloads' output — strip
  workload-supplied keys from the platform namespace, or a compromised agent
  can forge its own audit and cost attribution. Add the three attribution gaps
  as cautions on any "observability follows the agent" claim (Claim 12):
  platform-injected metadata cannot supply per-line trace context for a
  workload's own output; a last-write-wins lifecycle stream must never be
  sampled (dropping one record is "a correctness bug rather than a cost trade");
  and a collector that enriches by source IP will attribute an actor's spans to
  the gateway Pod that proxied them. **Verify which Pod your backend actually
  attributed a span to** before trusting per-agent attribution in a multiplexed
  deployment.

- **Chapter 06 (Security and Trust)**: Add per-actor default-deny egress as the
  attachment point for policy (Claim 16) — including the honest cost the
  project's own docs state: a default-deny egress policy means the agent's own
  telemetry stack is unreachable until explicitly granted, the grant must be
  `http` (not `https`) for OTLP, and applying it to a running actor costs 45s–2
  minutes of reconnect backoff. Contrast with the corpus's opposite default:
  `docs-litellm-a2a-agent-permissions.md` Claim 1 is **fail-open** when neither
  key nor team sets agent restrictions, so a guide recommendation on per-agent
  policy must name the default rather than say "add authorization." Add
  per-actor sandbox isolation with the sandbox runtime pinned by per-architecture
  hash (Claim 8) as the enforcement mechanism behind the deny-by-default posture,
  and note the limit: sandboxing plus scoped egress bounds the blast radius of
  the `blog-promptfoo-indirect-prompt-injection-web-agents.md` Claim 11 "lethal
  trifecta" but does not prevent an actor that holds all three capabilities from
  assembling it. Add the namespace-scoped credential-injection default (empty,
  default-deny, granted per tenant) as the complementary half to the
  host-bound credential pinning in `blog-litellm-lap-internal-agent-30-percent.md`
  Claim 5 — deny decides *which* secrets a tenant may read, pinning decides
  *where* a given credential may be sent.

- **Chapter 03 / Chapter 05 — the open-question list should be reproduced as-is.**
  The article's four questions (identity ownership, policy attachment point,
  ownership/quotas/billing across tenants, observability) are a better
  contribution than its conclusion (Claim 18). In particular the
  quota/billing question is the largest unresolved gap: `ate.atespace` provides a
  tenant boundary, but nothing in the article or the linked docs explains how a
  team is charged for actors that share a worker — and per-agent cost
  attribution is exactly what the observability design cannot put on metrics.
  The guide should state plainly that **"cheaper per agent" is not "chargeable per
  agent"**, and that this remains open.

- **Cross-cutting — adoption caveat the Smith should carry into any
  recommendation**: the implementation is `v1alpha1` from a pre-1.0 project with
  an explicit no-backward-compatibility guarantee, supporting only the latest
  stable Kubernetes release and the previous minor (Claim 19). The
  *pattern* — multiplexed workers behind a control plane that owns agent
  lifecycle — is the transferable contribution; the CRDs are not yet a
  standard-build target, and an N-2 Kubernetes cluster is out of scope.

## Extraction Notes

- **Linked pages followed** (5 attempted, 3 read in depth): the
  `agent-substrate` GitHub README, `docs/observability.md`, and
  `docs/request-parking.md` (all from the `agent-substrate/substrate` repo the
  article links in its "Looking Ahead" section) plus `agentgateway.dev`. Roughly
  half the concrete artifacts in this note come from the repo rather than the
  blog post — the blog carries no numbers at all, while the repo carries the
  density/latency figures, the observability design, and the parking mechanism.
  Every claim sourced from the repo names it in Evidence. Two linked URLs could
  not be read: `kagent.dev/docs/kagent/examples/agent-substrate` (the article's
  primary "learn more" link) returned **HTTP 500**, and the Christian Posta
  LinkedIn `/pulse/` post on agent identity is not fetchable. Neither is quoted.
- **Quote discipline**: every `Quote` was copied character-for-character from the
  fetched markdown of the page named in Evidence. Where a passage contained
  typographic quotes or markdown emphasis markers that would not survive into a
  quoted string, a contiguous sub-fragment carrying the same meaning was quoted
  instead of the whole sentence, and no two non-adjacent sentences were spliced
  (MINER.md §2a.3). Quotes containing the source's curly apostrophes (e.g. "aren't
  Kubernetes questions") are reproduced with the same characters. No quote in
  this note is a paraphrase.
- **`confidence_overall: emerging`** — not `settled`. The CRDs, CLI transcripts,
  and linked docs are concrete, checkable, and internally consistent, which is
  why Claims 1-2, 4-8, and 10-20 are graded `settled`. But the load-bearing
  *architectural conclusion* ("the Pod is the wrong deployment unit for agents")
  is a vendor's positioning argument with no benchmarks, no density
  methodology, no latency or cost measurements, and no migration or
  failure-postmortem material anywhere in the source set. Claim 9 is graded
  `anecdotal` for exactly that reason. `agent-substrate` is also pre-1.0 with an
  explicit no-stability guarantee.
- **Candidate cross-reference list** (`miner-related-notes.md`, 10 entries):
  all ten are lexical false positives — the retrieval matched on generic SRE
  vocabulary ("unit of work", "abstraction", "control plane", "burst"), not on
  agent deployment topology. Explicitly dismissed one line each:
  `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SLO
  granularity mismatch, no agent content.
  `docs-google-sre-eliminating-toil.md` — toil taxonomy, automation of toil, no
  agent content.
  `docs-google-sre-reliable-product-launches.md` — launch coordination and
  checklists, no agent content.
  `docs-google-sre-configuration-specifics.md` — config-as-programming-language
  pitfalls; matched only on "Kubernetes"/"sandbox" as config examples, nothing
  about agent deployment units.
  `docs-langfuse-roadmap.md` — Langfuse product roadmap (incl. planned
  agent-level trace views); relevant to agent observability as a *product*, but
  makes no claim about deployment units, identity binding, or scheduling, so not
  cited as a cross-reference.
  `docs-google-sre-prodcast-03-11-embracing-complexity.md` — sociotechnical
  complexity and "more whiteboards"; matched on "abstraction", nothing on agents.
  `docs-google-sre-data-processing-pipelines.md` — pipeline freshness/correctness
  SLOs and stage isolation; stage isolation is a different problem from agent
  isolation.
  `docs-google-sre-prodcast-03-13-imperative-declarative.md` — declarative vs.
  imperative config and Kubernetes as a declarative system; matched on
  "Kubernetes"/"Pod", no agent content.
  `docs-google-sre-on-call.md` — pager load and alert hygiene, no agent content.
  `docs-google-sre-slo-engineering-case-studies.md` — Evernote SLO adoption, no
  agent content.
  The Prospector's triage comment independently reached the same conclusion
  ("Existing notes that overlap: none. No source note covers kagent, Solo.io's
  agent-substrate, gVisor-based agent sandboxing, or Pod-vs-agent deployment
  units"), which this extraction confirms — the corpus's real neighbors
  (`blog-litellm-lap-internal-agent-30-percent.md`, `docs-litellm-a2a-agent-gateway.md`,
  `docs-google-sre-prodcast-04-10-platform-engineering.md`) were found by
  searching `source-notes/` directly and are cited above.
- **No contradiction issue filed.** Both candidate tensions were examined
  against the MINER.md §4a "when NOT to file" criteria and resolved as
  conditioning variables or as deliberate historical contrast — see the
  **Contradicts** bullet above for the reasoning on each. Checked
  `CONTRADICTIONS.md` (no entries yet) and all 15 open `contradiction`-labeled
  issues for prior coverage of this topic; none is on-topic.
- **Scope note for the Assayer**: this source's most valuable material is *not*
  in the blog post. The blog is a ~1,200-word architecture argument whose
  concrete content is two CRDs, one CLI transcript, and four open questions.
  The five claims a shallow read would produce (Pod-per-agent solved isolation /
  identity / policy / observability / scheduling; agents are idle so per-agent
  Pods waste resources; add a control plane above Kubernetes; observability must
  follow the logical agent; multi-tenancy and quotas are unsolved) are all
  present here — as Claims 2, 3, 4, 11, and 18 respectively — alongside fifteen
  more drawn from the project's own documentation. The one place where a reader
  could reasonably think the note overreaches is the density and resume-latency
  figures; those are quoted verbatim but graded `anecdotal` and explicitly
  marked in Guide Impact as not-to-be-reproduced-as-results.