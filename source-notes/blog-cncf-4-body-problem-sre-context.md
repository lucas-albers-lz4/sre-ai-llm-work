---
source_url: https://www.cncf.io/blog/2026/07/06/the-4-body-problem-of-sre-why-autonomous-operations-depend-on-context
source_type: blog-post
title: "The 4-body problem of SRE: Why autonomous operations depend on context"
author: "Sanjeev Sharma (Field CTO, StackGen; CNCF Member Post)"
date_published: 2026-07-06
date_extracted: 2026-10-07
last_checked: 2026-10-07
status: current
confidence_overall: anecdotal
issue: "#1618"
---

# The 4-body problem of SRE: Why autonomous operations depend on context

> A vendor-authored architecture essay arguing that autonomous operations are
> gated on context integration, not model capability: operational decisions
> span four "bodies of truth" (code, infrastructure state, runtime signals,
> operational knowledge) whose intersections no system owns, so the substrate
> (a unified, versioned knowledge graph) must come before agents, and every
> agent action must leave a decision trace recording inputs, policies, model
> version, and rejected hypotheses.

## Source Context

- **Type**: blog-post (CNCF Member Post — vendor-authored thought leadership)
- **Author credibility**: Sanjeev Sharma is Field CTO at StackGen (a vendor
  building an "agentic OS" in this space). Evidence base: one day-long
  practitioner working session in Bengaluru (senior SREs, platform engineers,
  engineering leaders), hallway conversations, and a single illustrative
  2 a.m. incident bridge narrative from the author's own past. The concept is
  credited to his own company's blog. No code, config, benchmarks, datasets,
  or architecture diagrams anywhere in the post. Prescriptions should be
  treated as argument, not practitioner-validated evidence.
- **Scope**: Covers the four-body context taxonomy, a failure-mode taxonomy
  for context-fragmented agents, the substrate-before-agents ordering claim,
  the decision-trace schema, and a metrics shift. Does NOT cover: how to
  build the knowledge graph (tooling, schema, ingestion), how to implement
  or store decision traces, autonomy gating/safety boundaries, evaluation,
  or any measured outcome. Post-dates the Dec-2025 corpus cutoff (2026-07-06).

## Extracted Claims

### Claim 1: The binding constraint on AI in operations is context availability, not model capability
- **Evidence**: Anecdotal — reported themes from a day of discussions,
  panels, and hallway conversations at a Bengaluru practitioner event. No
  benchmark, no comparative evaluation of models with/without context.
- **Confidence**: anecdotal
- **Quote**: "AI's biggest challenge in operations isn't model capability. It's context."
- **Our assessment**: We buy this as a framing device, and it is consistent
  with the corpus (context rot, context poisoning, connector/data-fabric
  patterns), but this post supplies zero measurement for it. The claim is
  also unfalsifiable as stated — "context" and "capability" are not
  independently varied anywhere in the source. Use as a principle candidate,
  not as evidence.

### Claim 2: Operational decisions span four coupled bodies of truth — code, infrastructure state, runtime signals, operational knowledge — and each is individually "mostly solved"
- **Evidence**: Architectural proposal. The four-body definitions are
  enumerated precisely; the "mostly solved" assessment is asserted, backed
  only by naming off-the-shelf tools (Git, Terraform, observability stack,
  Confluence). The intersection-failure claim is supported by the author's
  2 a.m. bridge anecdote (eight vendors, 200-row RACI, green dashboards per
  slice, root cause in an unintegrated subcontracted network telemetry
  stream).
- **Confidence**: emerging (as a taxonomy; the "mostly solved" sub-claim is
  anecdotal)
- **Quote**: "Each body, in isolation, is mostly solved (Git, Terraform, your observability stack, Confluence)."
- **Our assessment**: The taxonomy is useful and maps cleanly onto what the
  guide already treats separately (Ch02 runtime telemetry, Ch03 code/runbooks,
  change management, postmortems). We buy the division of labor. We do not
  buy "mostly solved" as a generalization — the corpus has ample evidence
  that each body individually has gaps (declared-vs-actual infra drift,
  stale runbooks). The load-bearing assertion is that failures live at the
  intersection where "the intersection is where we have historically had no
  system at all" (author's words), and that is plausible but unmeasured.

### Claim 3: Substrate before agents — a unified, real-time, versioned knowledge graph across all four bodies must exist before autonomous remediation is deployed
- **Evidence**: Architectural proposal + room consensus ("the room largely
  shared it"). No deployment data, no comparison of agent outcomes with vs.
  without the substrate. This is an ordering claim (integrate silos first,
  agents second) and the strongest testable prescription in the post.
- **Confidence**: emerging
- **Quote**: "You can't put an agent on top of four siloed, mutually-suspicious systems and expect reliability. An agent is only as good as the context it can reason over."
- **Our assessment**: Directionally consistent with the corpus's knowledge
  graph vs. RAG material, but stated as an absolute ordering rule without
  evidence of a failed rollout that violates it. Note the tension with
  corpus practice: several shipped agent products (PagerDuty SRE Agent,
  incident.io AI SRE) were deployed on connector-based context fabrics that
  are partial, not unified. Recommend the guide state this as a maturity
  gradient (context integration quality gates autonomy level) rather than a
  hard sequenced precondition — see Extends.

### Claim 4: Every agent action requires a durable decision trace recording inputs (graph snapshot), policies in effect, model version, rejected hypotheses, action, and outcome
- **Evidence**: Named as "the non-negotiable architectural commitment" — a
  proposed schema (six fields, listed by the author) with a compliance
  justification (CISO / risk officer / regulator). No example record, no
  storage format, no implementation.
- **Confidence**: emerging
- **Quote**: "The non-negotiable architectural commitment is the decision trace."
- **Our assessment**: This is the most concrete, reusable artifact in the
  post and the highest-value extraction. Two fields are genuinely new
  relative to the guide's current Ch06 rule (which logs tools / MCP servers
  / sub-agents): the versioned input snapshot ("which snapshot of the
  graph") and "the hypotheses it considered and rejected" — the latter is
  the difference between an action log and a reconstructable reasoning
  record. We buy the field list as a design proposal; we note it specifies
  nothing about retention, tamper-evidence, or storage, and that hypothesis
  capture in practice is the hardest field to record reliably (models do not
  reliably expose rejected hypotheses). Extend Ch06's rule with these fields;
  do not adopt the schema wholesale as settled.

### Claim 5: "A script with an LLM in the middle" is not production autonomy because prompt and model drift go uncaptured
- **Evidence**: Assertion with a concrete drift scenario (prompt changed
  Tuesday, model version bumped Thursday, input context never captured).
  No incident example of this specific failure.
- **Confidence**: emerging
- **Quote**: "a lot of impressive “autonomy” is a script with an LLM in the middle, where the prompt was different last Tuesday, the model version bumped on Thursday, and nobody captured the input context"
- **Our assessment**: The diagnostic criterion — behavior that "can't be
  reliably reproduced or audited" isn't autonomy — is a useful, sharp test
  and ties the anti-pattern directly to the decision-trace requirement
  (Claim 4): without versioned inputs and model/prompt versions, you have
  opaque automation. Corroborates the corpus's model/prompt versioning
  concerns (Honeycomb note's silent-provider-upgrade debugging) and gives
  Ch03 a crisp definitional line for what does NOT count as an agent.

### Claim 6: Fragmented context makes agents fail plausibly — errors that survive human review
- **Evidence**: War-room failure stories reported from the practitioner
  session ("Agents that confidently fix the wrong thing..."). No incident
  postmortem, no rate, no comparison condition.
- **Confidence**: anecdotal
- **Quote**: "When the context an agent reasons over is fragmented, it doesn't just fail. It plausibly fails, which is the kind of error that survives review."
- **Our assessment**: This is the post's genuinely non-obvious failure-
  mechanism claim: the danger of context fragmentation is not loud failure
  but review-passing failure — the mechanism by which context quality gates
  trust. We buy the mechanism as plausible (fragmented inputs yield
  locally-coherent, globally-wrong reasoning), but the source offers only
  anecdote. It complements rather than duplicates the corpus's "confidently
  wrong" material by naming *why* the error looks reasonable: every body the
  agent did see was self-consistent.

### Claim 7: Stale runbooks are arguably worse than no runbooks because they invite confident, wrong action
- **Evidence**: Assertion attributed to the room's discussions; no incident
  example, no mitigation offered beyond the substrate argument (the graph
  makes knowledge current by construction).
- **Confidence**: anecdotal
- **Quote**: "Stale runbooks are arguably worse than none, because they invite confident, wrong action."
- **Our assessment**: The asymmetry claim (a missing runbook forces human
  judgment; a stale runbook licenses autonomous wrong action) is logically
  sound and matters specifically once runbooks are packaged into agent
  skills — skill packaging freezes staleness into executable form. The
  source gives no evidence and no operational mitigation (no freshness
  signal, no invalidation mechanism). This is a caution to add to Ch03's
  skill-packaging guidance, not a reason to stop encoding runbooks.

### Claim 8: A three-item failure-mode taxonomy for context-fragmented agents: confidently fixing the wrong thing, demo-passes/production-breaks, unreconstructable reasoning
- **Evidence**: The agent failure stories surfaced in the practitioner
  session ("what no product deck includes"). Enumeration only.
- **Confidence**: anecdotal
- **Quote**: "Agents that confidently fix the wrong thing."
- **Our assessment**: Items 1 and 3 overlap claims elsewhere in the corpus
  (confidently-wrong; opaque automation), but the trio is a compact taxonomy
  useful for Ch03/Ch06 framing — notably, item 3 ("reasoning you can't
  reconstruct afterward") is precisely what the decision trace (Claim 4)
  remediates, so the post's structure is internally coherent: taxonomy →
  mechanism (Claim 6) → artifact (Claim 4).

### Claim 9: The knowledge graph must be versioned so every agent decision can be replayed against the exact snapshot it saw
- **Evidence**: Architectural requirement stated as a consequence of
  decision-making against a changing world; no implementation.
- **Confidence**: emerging
- **Quote**: "And it has to be versioned, because every agent decision is made against a specific snapshot, and you'll need to replay it."
- **Our assessment**: This is the technical hinge connecting Claims 3 and 4:
  the versioned snapshot is simultaneously the substrate's freshness
  mechanism and the decision trace's input field. Replayability of agent
  decisions against pinned snapshots is a strong, checkable design
  requirement that the corpus only touches indirectly. Buy it; it is the
  part of the schema most likely to be under-implemented in real systems.

### Claim 10: The metric worth watching shifts from recovery speed to incident-avoidance frequency
- **Evidence**: Forward-looking framing ("agents embedded in the path...
  incidents get rarer"), explicitly labeled a *consequence* of getting
  substrate and traces right, not a starting point. No data.
- **Confidence**: anecdotal
- **Quote**: "The number worth watching shifts from how fast you recover toward how often you never had a bad night."
- **Our assessment**: An aspirational reframing of MTTR-style metrics toward
  prevention. The post is explicit that this is downstream of substrate +
  traces ("It's not where you start"), which is intellectually honest.
  The corpus's SLO/error-budget material already treats prevention and
  recovery as complementary, so this adds vocabulary, not a contradiction.
  Low priority for the guide.

### Claim 11: Agents must be embedded in the path to production, not bolted on after it — a human doing the work while the agent writes the post-mortem is dictation, not autonomy
- **Evidence**: Assertion, framed as one of two closing principles.
- **Confidence**: anecdotal
- **Quote**: "“Human does the work, agent writes the post-mortem” isn't autonomy; it's dictation."
- **Our assessment**: A useful rhetorical distinction between agent-as-
  participant in the operational loop vs. agent-as-scribe, but it is a
  slogan without a criterion — where the line falls between "dictation" and
  legitimate human-supervised delegation is exactly what the corpus's
  investigation-vs-mitigation boundary (Zelesko note) addresses. Cite as
  framing; prefer the mutation-based boundary for actual guidance.

## Concrete Artifacts

The only structured artifacts in the source are enumerated lists. All
verbatim (CNCF blog post, 2026-07-06).

### The four bodies of truth (verbatim, as listed in the post)

```
- Code: Every commit, PR, branch, build artifact, version, and
  configuration change. What was deployed, when, and what was different
  from yesterday?
- Infrastructure state: The actual, current shape of cloud accounts,
  networks, Kubernetes clusters, queues, databases, and IAM policies.
  What does Terraform say should be there, and what is actually there,
  right now?
- Runtime signals: Metrics, logs, traces, events, error budgets, SLOs,
  and customer-impacting alerts. What is the system doing right this
  second, and when did it start behaving differently?
- Operational knowledge: The tribal wisdom, post-mortems, architectural
  decision records, on-call playbooks, the “we tried that in 2022 and
  took out the region,” the runbooks, the Slack threads that explained
  why a thing is the way it is.
```

### The decision-trace record (verbatim field list, as specified in the post)

```
For every action an agent takes, you need a durable record of:

- The inputs it saw (which snapshot of the graph)
- The policies in effect at the time
- The model version used
- The hypotheses it considered and rejected
- The action it took, and the outcome
```

### Closing principles (verbatim, as listed in the post)

```
- Treat operations as data. Stop letting code, infrastructure state,
  runtime signals, and operational knowledge live as four siloed,
  mutually-suspicious stacks. Integrate them into a unified knowledge
  graph you can query, version, and reason over. Agents come next, not
  first. Without that substrate, no agent will be trustworthy enough to
  put in the critical path.
- Embed agents in the path to production, not after it.
```

(Second bullet continues in the source with the dictation/autonomy
distinction quoted in Claim 11; truncated here for length.)

### The graph "edges" example (verbatim, as given in the post)

```
A commit changes a service. Terraform provisions new infrastructure.
Kubernetes rolls out the deployment. OpenTelemetry traces begin showing
increased latency while Prometheus records SLO burn. The graph connects
those events with a similar incident six months earlier and the
remediation that resolved it.
```

## Cross-References

- **Corroborates**:
  - [blog-pagerduty-production-ai-agent-gaps.md](blog-pagerduty-production-ai-agent-gaps.md)
    **Claim 13** (knowledge graphs with time/invalidation awareness needed
    for shared agent memory; RAG falls short) — the substrate claim here
    (Claim 3) is the same architectural conclusion reached at a higher level
    of abstraction and with *less* evidence; the PagerDuty note carries the
    concrete invalidation scenario. Also its **Claim 6** (context poisoning
    from "siloed, inconsistent, incomplete, and poorly structured" enterprise
    data) is the mechanism-level antecedent of this post's plausible-failure
    claim (Claim 6) — bad/fragmented context corrupts reasoning in both.
  - [docs-google-sre-ai-engineering-reliable-operations.md](docs-google-sre-ai-engineering-reliable-operations.md)
    **Claim 2** (Safety Trifecta: Transparency via chain-of-thought logging)
    — the decision trace (Claim 4) is a concrete field list for the
    Transparency pillar; **Claim 6** (IRM Analyzer reconstructs "hypotheses
    considered" from incident artifacts) independently confirms that
    rejected-hypothesis capture is a recognized record type in Google's
    production SRE AI system, not just this post's invention.
  - [blog-litellm-april-townhall-updates.md](blog-litellm-april-townhall-updates.md)
    **Claim 11** (organizations will treat agent auditability as a
    compliance expectation) — this post's compliance framing ("exactly what
    your CISO, your risk officer, and your regulator will ask for") is the
    same prediction with the schema attached.
  - [blog-honeycomb-instrumenting-ai-agents-opentelemetry.md](blog-honeycomb-instrumenting-ai-agents-opentelemetry.md)
    **Claim 7** (capturing requested vs. actual response model names to
    debug silent provider-side upgrades) — an implementable slice of the
    trace's "model version used" field (Claim 4), from the instrumentation
    side.

- **Contradicts**: None filed. The closest tension is with
  [blog-pagerduty-sre-agent-triage.md](blog-pagerduty-sre-agent-triage.md)
  **Claim 3** (teams encode runbooks into agent skills via
  `create-pagerduty-skill`): this post's Claim 7 says stale runbooks are
  arguably worse than none. These are conditioning variables, not opposing
  claims — skill-encoding presumes fresh runbooks; the post's point is about
  drift after the infra change lands. Both belong in Ch03 side by side
  (encode runbooks as skills AND give skills a staleness/freshness
  mechanism). Per MINER.md §4a this is a context difference, so no
  contradiction issue was filed.

- **Extends**:
  - [blog-litellm-april-townhall-updates.md](blog-litellm-april-townhall-updates.md)
    **Claim 11** is the source of Ch06's current auditability rule; this
    post's decision-trace field list (Claim 4) proposes the concrete
    extension of that rule's field enumeration (currently tools / MCP
    servers / sub-agents → add snapshot, policies, model version, rejected
    hypotheses, outcome).
  - [docs-promptfoo-enterprise-audit-logging.md](docs-promptfoo-enterprise-audit-logging.md)
    **Claim 6** shows a real audit schema that cannot answer "what did this
    actor remove?" because it records the request, not before/after state —
    the decision trace's versioned-input-snapshot field (Claim 9) is the
    design answer to exactly that structural gap (prior state is recoverable
    from the pinned snapshot). Conversely, the promptfoo note's warning
    applies to this post's schema: nothing here specifies a before/after
    diff either, so the guide should require both snapshot *and* outcome
    state.
  - [docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md](docs-google-sre-prodcast-06-04-zelesko-agentic-sre.md)
    **Claim 11** (dependency mapping should be a living, real-time
    understanding, not a point-in-time spec) is the incremental version of
    the substrate claim; this post escalates it from "living diagram" to a
    versioned, queryable, replayable graph. Its **Claim 5**
    (investigation-vs-mitigation as the autonomy boundary) supplies the
    safety criterion this post lacks — the post says when to trust agents
    (context) but not where to bound them (mutation).
  - [blog-incidentio-ai-sre-incident-run.md](blog-incidentio-ai-sre-incident-run.md)
    **Claim 10** (tool fragmentation and context switching as the friction
    in incident response) — a product-surface version of the four-body
    fragmentation problem at the human layer.
  - [blog-cncf-network-boundary-ai-agents-nginx-otel.md](blog-cncf-network-boundary-ai-agents-nginx-otel.md)
    **Claim 3** (every outbound agent request becomes an audited span at the
    proxy) — same publisher, different layer: that note's egress audit plane
    covers *where* an agent talked to; this post's decision trace covers
    *why it decided to*. Complementary layers of the same audit story; no
    content overlap.

- **Novel** (to our corpus):
  - The **four-body taxonomy** (code / infrastructure state / runtime
    signals / operational knowledge) as a named context model for SRE
    decisions, including the declared-vs-actual infra distinction ("what
    does Terraform say should be there, and what is actually there").
  - The **decision-trace schema with rejected hypotheses and versioned input
    snapshot** — no corpus source enumerates these fields (Google's IRM
    Analyzer reconstructs hypotheses *after the fact* for humans; this post
    wants them recorded *per agent action*).
  - The **substrate-before-agents ordering claim** as an explicit,
    testable sequencing rule.
  - The **plausible-failure mechanism** (fragmented context → errors that
    survive review) as distinct from generic "confidently wrong."
  - The **stale-runbook asymmetry** ("arguably worse than none") as a
    named failure mode for runbook/skill-based automation.
  - The **metric shift** from recovery speed to incident-avoidance
    frequency as a *downstream* consequence of context maturity.

## Guide Impact

- **Chapter 06 (Security and Trust)**: The existing rule ("Log the full
  agent decision trail — which tools were called, which MCP servers were
  consulted, what sub-agents were invoked", sourced to
  blog-litellm-april-townhall-updates Claim 11) should have its field list
  extended per this post's Claim 4: the graph/state **snapshot ID seen**,
  the **policies in effect**, the **model + prompt version**, the
  **hypotheses considered and rejected**, and the **action outcome**. The
  rejected-hypotheses and snapshot fields are the two the guide does not
  currently enumerate (Prospector's key question #2 — it holds up as a
  design proposal, flagged emerging/anecdotal in the source).
- **Chapter 03 (Runbooks and Agents)**: Two additions: (a) a staleness
  caution next to the skills-packaging guidance — packaging a runbook into a
  skill freezes drift into executable form; runbooks-as-skills need a
  freshness/invalidation signal (Claim 7, with
  blog-pagerduty-production-ai-agent-gaps Claim 13's invalidation-aware
  memory as the mechanism). (b) The "script with an LLM in the middle"
  anti-pattern (Claim 5) as a definitional line in the where-NOT-to-use-LLMs
  material: an LLM step with uncaptured prompt/model/input versions is
  opaque automation, not an agent — it fails the replay test of Claim 9.
- **Chapter 02 (Observability)**: The guide currently makes no dependency
  ordering assertion between context integration and agent rollout
  (verified: no "substrate first" / "integrate silos before agents" claim
  exists in guide/). This post supplies the corpus's first explicit ordering
  claim (Claim 3). Recommend the Smith consider stating it as a maturity
  gradient — context-integration quality gates the autonomy level granted —
  rather than the source's absolute "agents come next, not first," since
  shipped products in the corpus operate on partial context fabrics.
- **Chapter 00 (Principles)**: Optional principle candidate: "context, not
  capability, is the binding constraint" (Claim 1). Flagged anecdotal — only
  adopt if the Assayer judges the cross-corpus corroboration sufficient;
  this post alone does not carry it.

## Extraction Notes

- Source read in full via WebFetch of the single article URL; no sub-pages
  followed. The one outbound link (StackGen's own "4-Body Problem / agentic
  OS" blog) was deliberately NOT followed or propagated as evidence —
  it is the author's company marketing, per Prospector caveat. Everything
  quoted here is from the CNCF page itself.
- Quotes are contiguous fragments copied from the fetched source text;
  markdown emphasis markers present in the raw page (e.g. around
  "intersection" and "plausibly") were dropped to match rendered page text.
  No quote splices two non-adjacent sentences.
- **miner-related-notes.md candidates disposition** (10 listed): cited
  #2 `docs-google-sre-ai-engineering-reliable-operations.md` (Claims 2, 6)
  and #5 `docs-promptfoo-enterprise-audit-logging.md` (Claim 6). Explicitly
  dismissed: #1 `docs-google-sre-prodcast-03-07-retail-gaming.md` (retail/
  gaming SLO granularity — no topical claim overlap), #3
  `docs-google-sre-prodcast-03-13-imperative-declarative.md` (change-
  workflow styles — the "declared vs actual" adjacency is too thin to
  cite), #4 `docs-google-sre-prodcast-03-01.md`, #6
  `docs-litellm-batches-api.md`, #7 `docs-google-sre-eliminating-toil.md`,
  #8 `docs-google-sre-slo-engineering-case-studies.md`, #9
  `docs-google-sre-prodcast-02-07-sabrina-farmer.md`, #10
  `docs-litellm-completion-input-params.md` — lexical-retrieval noise, no
  shared claim with this source.
- Additional Prospector-flagged overlaps beyond the candidate list were
  searched and verified directly: blog-pagerduty-sre-agent-triage (Claims 3,
  9), blog-incidentio-ai-sre-incident-run (Claim 10), blog-honeycomb-
  instrumenting-ai-agents-opentelemetry (Claim 7), blog-cncf-network-
  boundary-ai-agents-nginx-otel (Claim 3), blog-litellm-april-townhall-
  updates (Claim 11), blog-pagerduty-production-ai-agent-gaps (Claims 6,
  13), docs-google-sre-prodcast-06-04-zelesko-agentic-sre (Claims 5, 11).
  All claim numbers re-checked against the cited notes' `### Claim:`
  headings per MINER.md §4b.
- No contradiction issue filed: the stale-runbook vs skill-encoding
  "tension" is a conditioning variable (see Cross-References), and no other
  claim in the source opposes an existing note's claim. No open
  contradiction issues were consulted for this topic since none surfaced.
- Evidence quality is the dominant limitation: no code, config, metrics, or
  diagrams in the source (Prospector's warning confirmed by direct read).
  confidence_overall set to `anecdotal` accordingly; individual claims
  graded emerging only where the architecture argument stands on its own
  logic rather than on the room's anecdotes.
