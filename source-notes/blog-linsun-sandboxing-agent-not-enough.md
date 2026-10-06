---
source_url: https://www.cncf.io/blog/2026/07/07/why-sandboxing-your-agent-is-not-enough
source_type: blog-post
title: "Why sandboxing your agent is not enough"
author: "Lin Sun (Solo.io, CNCF Ambassador)"
date_published: 2026-07-07
date_extracted: 2026-10-06
last_checked: 2026-10-06
status: current
confidence_overall: emerging
issue: "#1605"
---

# Why sandboxing your agent is not enough

> The kickoff post of the Lin Sun / CNCF series that argues Kubernetes-level
> sandboxing is a necessary but insufficient agent-hosting layer — isolation
> answers "can the agent escape?", not "should this agent be running at all?"
> — and, in passing, introduces the corpus's first coverage of the Kubernetes
> SIG Apps `agent-sandbox` project (a `Sandbox` CRD + controller) as the
> secure-execution counterpart to `agent-substrate`'s density/efficiency
> argument.

## Source Context

- **Type**: blog-post (CNCF blog, Ambassador Post). Architecture-positioning
  post; no code, YAML, or config in the article itself (one dashboard
  screenshot, the pool name `kagent-default`).
- **Author credibility**: Lin Sun, Solo.io, CNCF Ambassador. Solo.io is the
  creator of `agentgateway` and a co-founder of the `agent-substrate` project;
  `kagent` is the CNCF Sandbox project built on `agent-substrate`. First-hand
  knowledge of *what the projects do* (the artifacts are checkable against the
  repos), direct conflict of interest on *which architecture is right* — the
  article argues for its own project's abstraction. High credibility on
  description, low on the comparative conclusion.
- **Scope**: Covers (1) `agent-sandbox` (SIG Apps `Sandbox` CRD + controller)
  and its four focus areas, (2) `agent-substrate` at a summary level
  (density/efficiency/lifecycle, serverless-like suspend/resume), (3) the
  "necessary, but not sufficient" framing and the idle-agent resource tradeoff,
  (4) the head-to-head two-project framing with governance homes, (5) the
  six-AIRE-agents → one-worker-pod arithmetic. Does **NOT** cover: benchmarks,
  latency/cost figures, CVEs, incident forensics, exploit detail, migration
  guidance, or how the two projects integrate concretely (complementarity is
  asserted, not shown).
- **Linked pages followed for extraction** (per MINER.md §1; substrate
  material deliberately not re-read — the sibling note is authoritative):
  1. `https://github.com/kubernetes-sigs/agent-sandbox` (README) — the novel
     artifact: project scope, `Sandbox` CRD features, extensions
     (`SandboxTemplate` / `SandboxClaim` / `SandboxWarmPool`), install/verify,
     motivation, desired characteristics, SDKs, sandbox-router.
  2. `https://raw.githubusercontent.com/kubernetes-sigs/agent-sandbox/main/docs/security/threat_model.md`
     — trust boundaries, threat/mitigation tables, system-label protection,
     router SSRF posture. This is where the concrete isolation mechanics live;
     the blog has none.
  3. `https://raw.githubusercontent.com/kubernetes-sigs/agent-sandbox/main/roadmap.md`
     — 2026 priorities incl. auto suspend/resume, scale-to-zero (both
     *planned*), API maturity (`v1beta1` exclusive), completed warm-pool/HPA
     work.
  - `https://kagent.dev/docs/kagent/examples/agent-substrate` (article's
    "Get started" link) returned **HTTP 500** — same failure the sibling note
    recorded; not quoted.
  - The Christian Posta LinkedIn link and the Docker "horror stories" blog were
    not fetched (LinkedIn unfetchable per sibling note; the Docker post is
    cited as a generic pointer, not as evidence for any claim here).
  - `https://github.com/agent-substrate/substrate` not re-read: its content is
    already extracted to ~20 graded claims in
    `blog-linsun-pod-deployment-unit-ai-agent.md` (issue #1570), which the
    Prospector designated authoritative for substrate material.

## Extracted Claims

### Claim 1: `agent-sandbox` is a Kubernetes SIG Apps project providing a `Sandbox` CRD and controller, with four stated focus areas — strong agent identities, persistent storage surviving restarts, sandboxed-pod lifecycle management, and security/isolation via the Sandbox controller
- **Evidence**: The blog's project introduction, confirmed against the project
  README (same scope statement, SIG Apps link, Apache-2.0, releases to
  `v1.0.2`). The four focus bullets are the article's own enumeration.
- **Confidence**: settled (checkable against the repo; this is descriptive
  project fact, not an architectural opinion)
- **Quote**: "The agent-sandbox project provides a Sandbox Custom Resource Definition (CRD) and controller for Kubernetes under the umbrella of Kubernetes SIG Apps."
- **Quote**: "In short, agent-sandbox focuses on making agent execution secure, manageable, and Kubernetes-native."
- **Our assessment**: This is the genuinely new artifact for the corpus —
  nothing in `source-notes/` or `guide/` previously covered this project. Note
  the four focus areas map one-to-one onto what a Pod-per-agent deployment
  already gives you for free (identity via ServiceAccount, storage via PVC,
  lifecycle via the workload controller, isolation via the runtime) — the
  project's value proposition is doing it as *one* declarative object for
  singleton, stateful, network-accessible sandboxes, which the README states
  plainly: approximating this with "StatefulSets (size 1), Services, and
  PersistentVolumeClaims ... is cumbersome and lacks specialized lifecycle
  management like hibernation."

### Claim 2: `agent-sandbox` is a sandbox *orchestrator*, not an isolation implementation — low-level isolation is delegated to gVisor or Kata Containers via `RuntimeClass`, and the threat model says so explicitly
- **Evidence**: The README's scope note and the threat-model mitigation row
  for container escape.
- **Confidence**: settled (stated in both documents)
- **Quote**: "Agent Sandbox is a *sandbox orchestrator*. It delegates low-level container isolation to secure \"Sandbox Runtimes\" (like gVisor or Kata Containers) by managing Pods configured to use these runtimes (via `RuntimeClass`)."
- **Quote**: "Agent Sandbox itself does not implement isolation but supports configuring these runtimes."
- **Our assessment**: The blog's headline ("sandboxing your agent") slightly
  blurs this: the project's security story is only as strong as the
  `RuntimeClass` actually pinned in the template. The threat model names the
  enforcement path — platform admins put the secure runtime in a
  `SandboxTemplate` used by a `SandboxWarmPool`, so pools are pre-configured
  safe by construction; a bare `Sandbox` CRD created by a tenant leaves the
  runtime choice to the pod template. For Ch06: "we use agent-sandbox" is not
  a security claim until the enforced `runtimeClassName` is. This is the same
  division of labor the sibling note records for substrate (gVisor `runsc`
  pinned by per-architecture SHA256, its Claim 8) — two independent projects
  both landing on "Kubernetes for placement, gVisor/Kata for containment."

### Claim 3: Sandboxing is "necessary, but not sufficient" — isolation answers whether the agent can escape, while the unaddressed layer is idle-agent resource waste and the spin-up-latency tradeoff of always-on vs. on-demand agents
- **Evidence**: The article's central assertion, with the tradeoff spelled out
  as a two-option dilemma. No metrics: no idle fraction, no spin-up cost, no
  density numbers anywhere in the post.
- **Confidence**: emerging (per the Prospector's explicit grading instruction;
  sound reasoning, zero measurement)
- **Quote**: "Sandboxing your agents is necessary, but not sufficient."
- **Quote**: "Keep agents running idle and waste resources"
- **Quote**: "Or constantly spin them up and down, adding overhead and latency"
- **Quote**: "Neither option scales well."
- **Our assessment**: This is the transferable statement for Ch06 and the real
  contribution of the post: sandboxing answers "can the agent escape?", it
  does not answer "should this agent be running at all?" — the security layer
  and the efficiency layer are separate decisions and neither substitutes for
  the other. We buy the framing as a decision-structure; we do not buy it as
  evidence, because the "awkward tradeoff" is asserted with no numbers, and
  the dilemma's second horn (constant spin-up) is only a problem for
  controllers that do not batch, pool, or warm — which is exactly what both
  projects then propose as the fix. Grade `emerging`, not higher.

### Claim 4: The head-to-head framing — `agent-sandbox` asks "How do we run agents securely?", `agent-substrate` asks how to run them "efficiently at scale" — with `agent-sandbox` under Kubernetes SIG Apps and `agent-substrate` a standalone project with no SIG or foundation home
- **Evidence**: The article's "Final Thoughts" section for the two questions,
  and its own projects section for the governance homes. Governance facts are
  verifiable (SIG Apps repo path for one; the other's GitHub org is
  `agent-substrate/substrate`, outside kubernetes-sigs and cncf).
- **Confidence**: settled (the governance facts); the implied answer to "which
  do I need" is the vendor's position and stays `emerging` with Claim 3
- **Quote**: "Agent-sandbox asks: How do we run agents securely?"
- **Quote**: "The agent-substrate project is currently a standalone project and is not part of any Kubernetes SIG or other cloud native foundation project, though that may change in the future."
- **Quote**: "agent-sandbox and agent-substrate solve related but distinct problems."
- **Our assessment**: The two-question split is a clean decision frame for the
  guide: Ch06 picks the isolation baseline (which sandbox?), Ch03/Ch05 pick the
  hosting topology (which runtime model for an idle fleet?). The governance
  asymmetry is the load-bearing practical difference for adoption: a SIG Apps
  project carries upstream Kubernetes review, a defined API trajectory
  (Claim 10), and a community Slack/mailing list; the sibling note records
  substrate as pre-1.0 with an explicit no-backward-compatibility guarantee
  (its Claim 19). Note the article hedges its own comparison — "though that
  may change in the future" — so the governance gap is described as temporary,
  not structural.

### Claim 5: The article frames the two projects as complementary rather than competing — substrate keeps "a secure execution model" while adding density — but shows no integration artifact
- **Evidence**: The explicit comparison sentence in the "Do We Need
  Agent-substrate..." section, plus the kagent-integration section which
  describes intent ("discuss with our team how we could integrate it") rather
  than a shipped result. The `agent-sandbox` roadmap lists "Integration with
  Agentic Frameworks ... kAgent" as `⏳ In Progress`, not done.
- **Confidence**: emerging (assertion of complementarity; no architecture
  diagram, config, or code joining the two anywhere in the source)
- **Quote**: "While agent-sandbox focuses on security, isolation, and lifecycle management, agent-substrate focuses on density, efficiency, and operational scalability, while still preserving a secure execution model."
- **Our assessment**: "You can think of it as making large-scale agent fleets
  practical: not just safe, but economically viable" is the positioning
  conclusion, and it is exactly the conclusion a co-founder of one of the two
  projects would write. The complementarity claim deserves a skeptical read
  from the guide: nothing in this source shows the two projects composed — no
  `Sandbox` resource managed by a substrate worker, no shared identity model,
  no statement of which one owns the `RuntimeClass`. The `kagent` roadmap line
  is the only integration evidence and it is in-progress. Do not write "use
  agent-sandbox with agent-substrate" as guide advice on this source's
  authority alone.

### Claim 6: The concrete sizing example — six AIRE agents map to six actor templates but need only one worker pod when not running concurrently, with scale-out by adding `kagent-default` worker replicas
- **Evidence**: The author's personal setup (the AIRE agent suite in kagent),
  with a dashboard screenshot. No measured density, latency, or cost figure —
  this is a restatement of the substrate density claim the sibling note
  already graded `anecdotal` (its Claim 9), one week earlier in the series.
- **Confidence**: anecdotal (one author's deployment; the Prospector's explicit
  grading instruction)
- **Quote**: "For example, my six AIRE agents map to six actor templates but only require a single worker pod to execute them, as long as they are not running concurrently."
- **Quote**: "If concurrency increases, I can simply scale the worker pool (`kagent-default`) horizontally to increase the number of worker replicas."
- **Our assessment**: Useful as a concrete 6:1 sizing *example* and as an
  honest statement of the multiplexing precondition ("as long as they are not
  running concurrently") — the moment concurrency rises, the density ratio
  degrades to the pool size, and the fix is horizontal worker scaling, i.e.
  the density win is bounded by agent overlap, not by agent count. Carry it
  as an illustrative ratio in Ch03/Ch05, never as a benchmark. Do not
  duplicate the substrate mechanics behind it; the sibling note owns those.

### Claim 7: `agent-sandbox`'s documented default security posture — a managed default-deny NetworkPolicy per template (ingress only from the sandbox router, egress limited to the public Internet with RFC1918 and cloud-metadata endpoints blocked), `automountServiceAccountToken` defaulted to `false`, and resource limits expected from the template
- **Evidence**: The project's own threat model (trust boundaries + threat
  tables). Self-reported but specific and falsifiable — the invariant, the
  mechanism, and the operator warning are all named.
- **Confidence**: settled (documented defaults with named mechanisms)
- **Quote**: "When using `SandboxTemplate`, the controller provides a \"Managed NetworkPolicy\" mode (default) that automatically generates a strict shared NetworkPolicy: ingress is restricted to the Sandbox Router, and egress is restricted to the public Internet (blocking internal RFC1918 networks and cloud metadata endpoints)."
- **Quote**: "the controller automatically defaults `automountServiceAccountToken` to `false` when omitted"
- **Our assessment**: This is the concrete isolation content the blog article
  omits, and it is the reason to cite the threat model rather than the blog
  for Ch06. Three details matter for the guide: (1) the egress default blocks
  the cloud metadata endpoint — the exact path credential theft from a
  sandboxed agent would take (cf. the sibling note's default-deny per-actor
  egress, its Claim 16, achieved one layer down in substrate); (2) the posture
  is scoped to `SandboxTemplate` provisioning — a bare `Sandbox` gets no such
  defaults and the threat model says admins should use admission control
  (`ValidatingAdmissionPolicy`) to enforce them; (3) the docs warn the
  default-deny breaks sidecar health-check ports unless explicitly allowed —
  the same "secure-by-default costs you your own tooling" trade the substrate
  docs admit about telemetry egress. One incident-relevant warning: ingress is
  restricted *to the Sandbox Router*, so anything that bypasses the router
  (direct pod access, port-forward) is outside the managed policy's model.

### Claim 8: The threat model documents two control-plane threats specific to this design — Service-selector label spoofing as a cross-tenant traffic-hijack primitive (mitigated by system-key filtering) and a router SSRF posture whose only defense today is an IP-class check because the default authorizer is `AllowAll`
- **Evidence**: The threat model's "System Label and Annotation Protection"
  section (attack walkthrough, per-path mitigations) and the Router Proxy Abuse
  mitigation row. The project documents its own gap rather than hiding it.
- **Confidence**: settled (self-reported threat + named mitigation + named
  open gap)
- **Quote**: "Tenant B's Pod now also matches Sandbox A's Service selector, so traffic intended for Sandbox A can be delivered to the attacker's Pod (a network-isolation bypass / traffic-hijack primitive)."
- **Quote**: "since the default authorizer is `AllowAll` (for Python client compatibility), this IP-class check is currently the *only* SSRF defense."
- **Our assessment**: High-value Ch06 material with a general lesson: any
  controller that propagates user-supplied template labels onto Pods it
  manages owns a label-injection threat, and the reserved-namespace pattern
  here (`agents.x-k8s.io/*` filtered on create *and* adoption, selector label
  assigned after merge) is the same shape as substrate's anti-spoofing rule
  for `ate.*` metadata (sibling note Claim 14) — two projects independently
  arriving at "platform namespaces are reserved; strip workload-supplied
  keys." The `AllowAll` router authorizer is the honest weak spot: the blog
  sells isolation, the threat model says the router's SSRF defense currently
  rests on one IP-literal check, and operators are told to configure a custom
  authorizer. Any guide recommendation to adopt the project should carry that
  precondition.

### Claim 9: The article's entire failure discussion is a generic appeal to horror stories — no benchmark, CVE, exploit, or incident appears anywhere in the source
- **Evidence**: The security-motivation paragraph cites a Docker blog round-up
  and community projects by name; the concrete failure mode given is household,
  not technical.
- **Confidence**: anecdotal (this claim is about the *absence* of evidence —
  verified by full read of the article)
- **Quote**: "Without proper isolation, agents can surprise you by doing things you never intended, such as deleting family photos or modifying critical files."
- **Our assessment**: Carry this as an explicit non-claim, per the Prospector's
  caveat: the post has no benchmarks, no incident forensics, no CVE, no
  exploit. "Sandboxing is necessary" is argued from plausibility, not from any
  observed escape. The guide may use the framing (Claim 3) but must not cite
  this post as evidence that agent sandbox failures happen or how they happen —
  for that the corpus has `blog-promptfoo-indirect-prompt-injection-web-agents.md`
  (tested attack classes) and the Google SRE prodcast guardrail note.

### Claim 10: Maturity contrast — `agent-sandbox` is `v1beta1`-only with `v1alpha1` removed, ships at release `v1.0.2` with Go/Python SDKs, while `agent-substrate` remains pre-1.0 with no stability guarantee
- **Evidence**: The `agent-sandbox` roadmap's completed "Alpha to Beta API
  Versioning" entry, the README's versioned install commands (`v1.0.2`, Go SDK
  via `sigs.k8s.io/agent-sandbox`, Python via `k8s-agent-sandbox`), against the
  substrate README status section as recorded in the sibling note's Claim 19.
- **Confidence**: settled (both statements verifiable in the respective repos)
- **Quote**: "`v1beta1` is the exclusive served API version across all CRDs. Legacy `v1alpha1` types, conversion webhooks, and migration harnesses have been removed."
- **Our assessment**: The most decision-relevant difference for an adopter,
  and neither blog post makes it — it comes from reading both projects'
  repos. Sibling note Claim 19 records substrate as `v1alpha1`,
  pre-1.0, "not making any guarantees about backward compatibility," supporting
  only latest-stable Kubernetes + previous minor; agent-sandbox has already
  crossed to `v1beta1` with legacy types deleted, is installable by pinned
  release manifest, and offers versioned client SDKs. The guide's adoption
  caveat should distinguish the two maturity levels rather than lumping "the
  two agent-hosting projects" together.

## Concrete Artifacts

### Minimal `Sandbox` — verbatim from the `agent-sandbox` README (Getting Started)

```yaml
apiVersion: agents.x-k8s.io/v1beta1
kind: Sandbox
metadata:
  name: my-sandbox
spec:
  podTemplate:
    spec:
      containers:
      - name: my-container
        image: <IMAGE>
```

> Note the API group: `agents.x-k8s.io/v1beta1` — distinct from substrate's
> `ate.dev/v1alpha1`. The blog article gives no YAML at all; this and every
> artifact below come from the linked project repo.

### Project scope note — verbatim from the `agent-sandbox` README

```
**Scope:** Agent Sandbox is a *sandbox orchestrator*. It delegates low-level
container isolation to secure "Sandbox Runtimes" (like gVisor or Kata
Containers) by managing Pods configured to use these runtimes (via
`RuntimeClass`).
```

### Extension CRDs — verbatim from the `agent-sandbox` README

```
*   `SandboxTemplate`: Provides a way to define reusable templates for creating Sandboxes, making it easier to manage large numbers of similar Sandboxes.
*   `SandboxClaim`: Allows users to create Sandboxes from a `SandboxWarmPool`, abstracting away the details of the underlying Sandbox configuration.
*   `SandboxWarmPool`: Manages a pool of pre-warmed Sandboxes that can be quickly allocated to users, reducing the time it takes to get a new Sandbox up and running.
```

### Install / verify — verbatim from the `agent-sandbox` README

```sh
# Quick install (latest release):
kubectl apply -f https://github.com/kubernetes-sigs/agent-sandbox/releases/latest/download/sandbox-with-extensions.yaml

# Check for agent-sandbox CRDs
kubectl get crd sandboxes.agents.x-k8s.io

# Check for the controller deployment
kubectl get deploy agent-sandbox-controller -n agent-sandbox-system
```

### Threat-model mitigation rows (container escape, K8s API abuse) — verbatim from `docs/security/threat_model.md`

```
**Recommendation:** Use secure container runtimes (e.g., gVisor, Kata Containers) via `RuntimeClass` in the `PodTemplate`. Agent Sandbox itself does not implement isolation but supports configuring these runtimes. <br>**Enforcement:** Platform administrators can enforce this by defining templates in a `SandboxTemplate` (used by a `SandboxWarmPool`) that pre-configure the secure `runtimeClassName`.
```

```
**Mitigation:** When provisioned via a `SandboxTemplate`, the controller automatically defaults `automountServiceAccountToken` to `false` when omitted. Explicitly setting it to `true` is an opt-in security exception. For bare `Sandbox` CRDs, administrators should use admission control (like `ValidatingAdmissionPolicy`) to enforce this.
```

### Roadmap maturity + planned efficiency items — verbatim from `roadmap.md`

```
**Alpha to Beta API Versioning** `✅ Done`
    `v1beta1` is the exclusive served API version across all CRDs. Legacy `v1alpha1` types, conversion webhooks, and migration harnesses have been removed.
```

```
**Auto Suspend/Resume** `📅 Planned`
    Automatically suspend inactive sandboxes and resume them upon traffic or API invocation.

**Scale to Zero** `📅 Planned`
    Suspend sandboxes when inactive, preserving underlying resources while maintaining rapid resume paths.
```

> These are marked *Planned*, not done — relevant to Claim 5: the efficiency
> axis is on `agent-sandbox`'s own roadmap, which softens the blog's clean
> two-project dichotomy.

## Cross-References

- **Corroborates**:
  - `blog-cncf-network-boundary-ai-agents-nginx-otel.md` (Claim 1 — the
    boundary must be architectural, "a property of the architecture, not a
    policy we hope the application respects"). The managed NetworkPolicy +
    router-only ingress + metadata/RFC1918 egress block (Claim 7) is the same
    principle implemented as a Kubernetes controller default instead of
    iptables+proxy. That note's Claim 4 caveat also lands here: "Restricting
    where an agent can communicate does not guarantee that its decisions are
    correct or safe" — network/isolation control is not intent control, which
    is precisely why this source's "necessary, but not sufficient" (Claim 3)
    applies one layer further down.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` (Claim 3 — the default
    guardrail is to deny agents any world-mutating action, "writes run in a
    sandbox, and anything that breaks the sandbox needs an additional check").
    `agent-sandbox` is that sandbox as a Kubernetes primitive; the prodcast's
    "anything that breaks the sandbox needs an additional check" is the same
    insufficiency claim this article makes from the efficiency side — the
    sandbox bounds impact, it does not certify the agent.
  - `blog-litellm-lap-internal-agent-30-percent.md` (Claim 1 — separating a
    persistent "brain" pod from ephemeral per-session sandboxes reduces
    latency, raises success rate, lowers cost). Independent, non-Kubernetes
    arrival at the same layering: a stable identity/control surface plus
    disposable isolated execution environments. `agent-sandbox` is the
    declarative-Kubernetes packaging of the ephemeral-half.
- **Contradicts**: None, and no contradiction issue filed. One tension was
  examined against MINER.md §4a and resolved as a *nascent overlap*, not a
  disagreement: the article's dichotomy — sandboxing handles security,
  substrate handles efficiency (Claims 3–5) — sits awkwardly beside
  `agent-sandbox`'s own roadmap, which lists Auto Suspend/Resume and
  Scale-to-Zero as planned items and already shipped HPA + cold-standby
  cost reduction. Both projects are converging on the idle-agent problem from
  opposite ends; that is roadmap competition, not contradictory claims about
  fact, and neither side's claim would lead to different guide advice today
  (the planned items are not implemented). Checked `CONTRADICTIONS.md` (no
  entries) before deciding.
- **Extends**:
  - `blog-linsun-pod-deployment-unit-ai-agent.md` (issue #1570) — the sibling
    note and this one are two halves of one series. That note owns all
    `agent-substrate` mechanics (`WorkerPool`/`ActorTemplate`, request parking,
    `ate.*` observability, egress defaults, density figures — its Claims 4–20);
    this note adds the `agent-sandbox` half (Claims 1, 2, 7, 8, 10) and the
    series' framing claims (3–5). Specifically extends its Claim 8 (substrate
    pins gVisor by hash) and Claim 14 (reserved `ate.*` namespace stripped of
    workload-supplied keys): `agent-sandbox` independently lands on the same
    two patterns — runtime delegated to `RuntimeClass` and system-reserved
    `agents.x-k8s.io/*` labels filtered on create and adoption (Claim 8 here).
    Its Claim 19 (substrate pre-1.0, no stability guarantee) now has the
    contrast pair in Claim 10 here (`v1beta1`, v1.0.2, SDKs).
  - `blog-promptfoo-indirect-prompt-injection-web-agents.md` (Claim 11 — the
    "lethal trifecta" of private data access + untrusted content + external
    communication). `agent-sandbox`'s default-deny egress with metadata-endpoint
    blocking (Claim 7) structurally constrains the external-communication leg
    and the blast radius of the private-data leg — with the same limit the
    promptfoo note implies: a sandbox granted the egress it needs can still
    assemble all three legs, so containment bounds impact rather than
    preventing the trifecta.
- **Novel** — first coverage in the corpus of:
  - **The Kubernetes SIG Apps `agent-sandbox` project**: `Sandbox` CRD at
    `agents.x-k8s.io/v1beta1`, the controller, and the extension CRDs
    `SandboxTemplate` / `SandboxClaim` / `SandboxWarmPool` (grep confirmed no
    prior hit in `source-notes/` or `guide/`).
  - **The sandbox-orchestrator decomposition**: isolation delegated to
    `RuntimeClass`-selected gVisor/Kata, with the project explicitly not
    implementing isolation itself.
  - **A published agent-sandbox threat model** with trust boundaries, per-threat
    mitigation tables, the Service-selector label-spoofing attack walkthrough,
    and self-declared gaps (router `AllowAll` authorizer).
  - **The "necessary, but not sufficient" security-vs-efficiency framing for
    agent hosting** — sandboxing answers escape risk; the idle-resource /
    spin-up-latency layer is separate and unaddressed by isolation.
  - **Warm pools as the spin-up-latency answer inside the sandbox layer**
    (`SandboxWarmPool` pre-warms, claims adopt from pools) — the corpus's
    first warm-pool artifact for agent execution environments.
  - **The governance-home comparison**: SIG Apps project vs standalone
    pre-1.0 project as an adoption criterion.

## Guide Impact

- **Chapter 06 (Security and Trust)**: Two additions.
  (1) **Name `agent-sandbox` as the Kubernetes-native isolation baseline for
  agent workloads**, with the claim's own limit attached: isolation is
  necessary, not sufficient (Claim 3) — Ch06 should state explicitly that
  sandboxing answers "can the agent escape?" while a separate layer must
  answer "should this agent be running at all?". Cite the threat model, not
  the blog, for the mechanics: managed default-deny NetworkPolicy with
  cloud-metadata egress blocked, `automountServiceAccountToken` defaulted
  false, secure runtime via enforced `runtimeClassName` in `SandboxTemplate`
  (Claims 2, 7) — and carry the precondition that bare `Sandbox` CRDs get
  none of these defaults, so template/admission enforcement is part of the
  recommendation.
  (2) **Add the reserved-namespace pattern as a corpus-wide rule**: two
  independent projects now strip workload-supplied keys from platform-owned
  label/metadata namespaces to prevent attribution spoofing and
  cross-tenant traffic hijack (Claim 8 here; sibling note Claim 14 for the
  log-metadata variant). Pair with `blog-cncf-network-boundary-ai-agents-nginx-otel.md`
  Claim 4 — network/isolation control is not intent control — as the boundary
  of what this layer buys.
- **Chapter 03 (Runbooks and Agents)**: Extend the agent-hosting topology
  decision (which the sibling note introduced as Pod-per-agent vs multiplexed
  workers) with the *isolation* axis: pick the sandbox/`RuntimeClass` layer
  first (this source, `agent-sandbox` as the declarative option), then the
  hosting topology (sibling note). Add the six-agents/one-worker-pod example
  (Claim 6) as an illustrative sizing ratio explicitly labeled anecdotal,
  with its precondition ("as long as they are not running concurrently") and
  its remedy (scale `kagent-default` replicas) stated — density is bounded by
  concurrency overlap, not agent count. Note the warm-pool/claim pattern
  (Concrete Artifacts → Extension CRDs) as the runbook answer to
  "spin-up latency" when agents must wake on invocation.
- **Chapter 05 (LLM Ops Reliability)**: Add the idle-dilemma framing (Claim 3)
  as the *decision trigger* for on-demand agent hosting: agents that are
  "only useful occasionally" plus constrained resources is the condition under
  which always-on Pods are waste; pair with the sibling note's Claim 3
  (task-triggered / approval-gated agents) for the fuller trigger list. Carry
  the explicit non-claim: this source contributes no benchmarks, no latency
  figures, and no failure data (Claim 9) — density and resume numbers in the
  guide come only from the sibling note's Claim 9 and stay graded
  `anecdotal`.
- **Cross-cutting — adoption caveat**: keep the two projects' maturity levels
  distinct (Claim 10): `agent-sandbox` at `v1beta1`/v1.0.2 with SDKs and a
  SIG Apps home versus `agent-substrate` pre-1.0 with no stability guarantee
  (sibling Claim 19). The guide should not present them as interchangeable
  maturity, and should not recommend composing them (Claim 5) until an
  integration artifact exists.

## Extraction Notes

- **Delta-only extraction per the Prospector's scope**: no
  `agent-substrate` control-plane mechanics were re-extracted —
  `WorkerPool`/`ActorTemplate`/`Worker`/`Actor`, `ate.dev/v1alpha1`,
  request parking, `ate.*` observability, and egress defaults all live in
  `blog-linsun-pod-deployment-unit-ai-agent.md` (#1570) and are cited there,
  not duplicated here. The one substrate statement quoted in Claim 6 (the
  six-agent arithmetic) is the article's own restatement, graded `anecdotal`
  independently.
- **Quote discipline**: every `Quote` was copied character-for-character from
  the fetched markdown of the page named in its Evidence field (blog text from
  the CNCF page; project text from the raw GitHub README / threat model /
  roadmap). Markdown link syntax and emphasis markers inside quoted passages
  were reduced to their rendered text (e.g. the SIG Apps link renders as
  "SIG Apps"; `*only*` renders as "only" where quoted as prose) — no wording,
  punctuation, or clause order was altered, and no two non-adjacent sentences
  were spliced (MINER.md §2a). Quotes retain the source's straight quotes and
  backticked identifiers as they appear in the raw files.
- **`confidence_overall: emerging`** — Claims 1, 2, 4 (governance facts), 7,
  8, and 10 are `settled` because they are checkable artifacts and documented
  defaults in the linked repos. The article's load-bearing conclusion —
  sandboxing is insufficient and substrate-style density is required — is a
  vendor's positioning argument with zero measurements behind it (Claims 3, 5
  `emerging`; Claims 6, 9 `anecdotal`), consistent with the sibling note's
  `emerging` overall grade.
- **Candidate cross-reference list** (`miner-related-notes.md`, 10 entries):
  all ten are lexical false positives — the retrieval matched on generic SRE
  vocabulary, not on agent sandboxing or hosting topology. Explicitly
  dismissed one line each:
  `docs-google-sre-prodcast-03-07-retail-gaming.md` — retail/gaming SLO
  granularity, no agent content.
  `docs-google-sre-eliminating-toil.md` — toil taxonomy, no agent content.
  `docs-google-sre-prodcast-03-13-imperative-declarative.md` — declarative vs.
  imperative workflows; matched on "Kubernetes"/"declarative", no agent
  content.
  `docs-google-sre-reliable-product-launches.md` — launch coordination, no
  agent content.
  `docs-google-sre-on-call.md` — pager load and alert hygiene, no agent
  content.
  `docs-litellm-anthropic-advisor-tool.md` — advisor-tool token accounting,
  no sandbox or hosting content.
  `docs-litellm-completion-function-call.md` — LiteLLM capability flags, no
  sandbox content.
  `docs-google-sre-configuration-specifics.md` — config-as-language pitfalls;
  its "sandboxing" hits are about hermetic config evaluation, and its
  "agent-sandboxing guidance" phrase is a generic pointer, not the SIG Apps
  project (grep confirms this note is the corpus's only `agent-sandbox`
  string hit and it is unrelated).
  `docs-google-sre-prodcast-04-05-furino-slos.md` — SLO/error-budget
  definitions, no agent content.
  `docs-google-sre-prodcast-05-04-del-cid-ai-sre.md` — Google AI-for-SRE tooling;
  no sandbox/hosting content.
  The corpus's real cross-references (sibling note, NGINX boundary note,
  Google guardrail prodcast, LiteLLM brain/sandbox split, promptfoo trifecta)
  were found by searching `source-notes/` directly and are cited above after
  re-reading each cited claim (MINER.md §4b).
- **No contradiction issue filed** — see the **Contradicts** bullet for the
  one examined tension and why it fails the §4a bar (roadmap convergence, not
  opposing claims).
- **Unreadable link**: `kagent.dev/docs/kagent/examples/agent-substrate`
  returned HTTP 500 at extraction time (2026-10-06), matching the sibling
  note's record. The article's two "Additional Resources" that could not be
  read are not quoted anywhere in this note.
