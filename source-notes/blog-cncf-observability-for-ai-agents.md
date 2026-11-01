---
source_url: https://www.cncf.io/blog/2026/08/04/you-cant-debug-what-you-cant-see-observability-for-ai-agents
source_type: blog-post
title: "You can't debug what you can't see — Observability for AI Agents"
author: Sabith K Soopy (Principal Engineer, StackGen)
date_published: 2026-08-04
date_extracted: 2026-11-01
last_checked: 2026-11-01
status: current
confidence_overall: emerging
issue: "#1943"
---

# You can't debug what you can't see — Observability for AI Agents

> A CNCF Member Post practitioner report arguing that agent operations need a
> three-pillar observability model — agent traces, token cost, and an immutable
> audit log — with pre-flight circuit breakers (iteration caps, per-tool budgets,
> identical-call loop detection) placed *before* alerting, cost-anomaly alerting
> against a rolling average, and a hard cardinality rule against putting session
> IDs in Prometheus labels.

## Source Context

- **Type**: blog-post (CNCF Member Post; practitioner experience report)
- **Author credibility**: Sabith K Soopy is a Principal Engineer at StackGen. The
  post carries the CNCF Member Post byline and describes itself as reflecting
  "practical experience building and operating production AI agent systems" over
  "months" of production operation. Credibility is practitioner-level, not
  measured-research-level: the author names the trace backend (Langfuse) and the
  exact operational mechanisms, but presents no incident counts, latency
  distributions, bill deltas, or before/after metrics. StackGen is a commercial
  vendor, but the post is not a product pitch and does not describe StackGen's
  product.
- **Scope**: Covers the three observability pillars for agents (traces, costs,
  audit), the argument that standard APM answers the wrong questions, pre-flight
  loop/cost guardrails, cost alerting against a rolling average, the Prometheus
  cardinality trap for session identifiers, non-blocking trace export, a
  `brew doctor`-style diagnostic command, automated review of completed traces,
  and a bounded metrics set. Does **not** cover: OpenTelemetry GenAI semantic-
  convention attribute names, concrete alert thresholds/formulas beyond "a
  multiple of the rolling average," SLO definitions, or any quantitative result.
- **Maturity caveat**: This is a pattern report, not an evaluation. Per the
  Prospector's triage, claims are capped at `emerging` despite the production
  provenance because no numbers are given.

## Extracted Claims

### Claim 1: Traditional APM cannot answer the questions agent operators actually need answered
- **Evidence**: The author contrasts three standard monitoring questions (is the
  service up, how fast, are there errors) with five agent-specific questions:
  why a task cost more, why a tool was called repeatedly, whether the agent did
  what it said, which model fits a task type, and whether the agent is learning
  or repeating mistakes.
- **Confidence**: emerging
- **Quote**: "Agents don't crash with stack traces. They loop, hallucinate, burn tokens, and produce plausible-looking output that's subtly wrong."
- **Our assessment**: The failure-mode shift is the useful part: agent failures
  are often *successful-looking* outputs with bad economics or bad semantics,
  which standard request/error/latency monitoring cannot surface. The paired
  quote "Prometheus counters and Grafana dashboards alone won't answer them" is
  directionally right for the *why* questions, though the article's own answer
  still uses Prometheus counters for the bounded alerting signals (Claim 10) —
  so read this as "APM alone is insufficient," not "metrics are useless."

### Claim 2: Every agent session should produce an agent trace capturing each model call, tool call, and sub-agent delegation with timing and cost attached
- **Evidence**: The article defines an "agent trace" as the full decision history
  rather than a generic APM trace, and says sub-agent work nests as child spans
  under the parent trace so delegation can be followed without losing the thread.
  The author names Langfuse as the trace backend in use.
- **Confidence**: emerging
- **Quote**: "Every agent session should produce a trace — not a generic APM trace, but an agent trace that captures the full decision history: each model call, each tool invocation, each sub-agent delegation, with timing and cost attached."
- **Our assessment**: This is the article's structural core and it agrees with
  the corpus's OTel GenAI instrumentation material: the unit of debugging is the
  session/agent execution graph, not the individual LLM request. The addition
  here is that *cost* is attached to the trace at span level, making the trace
  answer economic questions as well as sequencing questions. No span schema or
  attribute names are given, so this is a modeling principle rather than an
  implementation contract.

### Claim 3: Trace delivery must be non-blocking — buffer spans in memory, flush in batches, drain gracefully on shutdown, and lose telemetry rather than availability if the backend is unreachable
- **Evidence**: The author states the requirement directly and prescribes a batch
  exporter pipeline with in-memory buffering, periodic flush, and a shutdown
  drain; the stated failure trade-off is explicit.
- **Confidence**: emerging
- **Quote**: "If the trace backend is temporarily unreachable, you lose telemetry — not availability."
- **Our assessment**: A sound reliability rule and one the tracing-focused corpus
  notes do not state explicitly. It correctly makes the observability plane
  subordinate to the serving path: a trace backend outage must not become an
  agent outage. The article does not discuss buffer sizing, backpressure when the
  buffer fills, or sampling, so the operational details remain open; the
  principle (async export, bounded loss) is the transferable part.

### Claim 4: Token cost is the unit economics of agents, and loops burn tokens geometrically
- **Evidence**: The cost pillar defines two visibility levels — per session
  (total cost, token breakdown, which model did what) and per agent over time
  (daily burn, session count, cost trends) — and explains that a looping agent
  repeatedly calling the same tool "burns tokens geometrically."
- **Confidence**: emerging
- **Quote**: "Token costs are the unit economics of agents."
- **Our assessment**: Framing cost as unit economics rather than a billing
  afterthought is the right posture for LLM ops, and the "geometrically" claim is
  mechanically plausible for a loop that adds a model call plus tool output to
  context on each iteration. There is no measurement of the multiplier, so the
  guide should teach the mechanism and the monitoring requirement, not a specific
  burn rate.

### Claim 5: Pre-flight circuit breakers — hard iteration caps, per-tool-call budgets, and loop detection that blocks identical consecutive calls — are the first line of defense, with alerting second
- **Evidence**: The author's explicit ordering argument: a tight loop in a
  parallel agent can burn budget in seconds, before a webhook fires, so reactive
  alerting cannot be the primary control.
- **Confidence**: emerging
- **Quote**: "Hard iteration caps, per-tool call budgets, and loop detection that blocks identical consecutive calls all act as pre-flight circuit breakers. Alerts are the second line of defense, not the first."
- **Our assessment**: This is the highest-value operational claim in the source,
  and it inverts the usual alert-first framing: the control must execute inside
  the request path, before the spend happens, because alert delivery latency is
  longer than the burn time of a parallel loop. The three named mechanisms are
  concrete enough to implement. The article gives no cap values, no false-positive
  analysis for "identical consecutive calls" (a legitimate retry pattern could be
  blocked), and no measured burn rate — so the ordering argument is strong while
  the parameterization is unresolved.

### Claim 6: Alert when a single session exceeds a multiple of the rolling average cost for that agent — this catches slower-burning anomalies that hard limits miss
- **Evidence**: The author names the alert condition and the anomaly classes it
  is meant to catch: hallucination spirals, model routing errors, and gradually
  accumulating context.
- **Confidence**: emerging
- **Quote**: "Alert when a single session exceeds a multiple of the rolling average cost for that agent. This catches slower-burning anomalies — hallucination spirals, model routing errors, gradually accumulating context — that slip past hard limits."
- **Our assessment**: A concrete and implementable alert definition, and a useful
  complement to the pre-flight caps: hard caps bound the worst case, the rolling-
  average comparison catches sessions that stay under the cap but are still
  economically abnormal for that agent. The article does not specify the
  multiplier, the rolling window, the per-agent baseline construction, or how to
  handle low-volume agents whose averages are noisy — those are the hard parts of
  operationalizing it. It is a curated relative threshold, not a generalized
  anomaly detector (see Cross-References to the Google alerting note).

### Claim 7: Every tool call, governance decision, and memory operation should be written to an append-only, structured, timestamped, searchable audit record
- **Evidence**: The audit pillar names the three event classes and the required
  record properties; the stated purpose is reconstructing what happened during
  incident review without exposing credentials.
- **Confidence**: emerging
- **Quote**: "Every tool call, governance decision, and memory operation should log to an append-only record — structured, timestamped, searchable."
- **Our assessment**: The scope is broader than typical application logging:
  including *governance decisions* and *memory operations* makes the audit trail
  cover the agent's decision layer, not just its I/O. Append-only is the right
  default for an evidentiary record. The article does not discuss retention,
  tamper-evidence, or access control on the audit store, so the guide should treat
  those as required follow-ons rather than assuming this sentence covers them.

### Claim 8: A doctor-style one-shot diagnostic command should check every agent dependency and report clear pass/fail
- **Evidence**: The author describes a `brew doctor`-style command in production
  use that checks model connectivity, vector store reachability, pending
  approvals, memory counts, trace backend status, and integration health.
- **Confidence**: emerging
- **Quote**: "We built a doctor-style diagnostic command (think brew doctor) that checks agent health in one shot: model connectivity, vector store reachability, pending approvals, memory counts, trace backend status, and integration health."
- **Our assessment**: A practical, low-cost operational tool with a clear
  rationale — "no digging through five dashboards to find which dependency is
  down" — and a dependency list that generalizes to most agent stacks. It is an
  operator convenience rather than a measured reliability improvement; the guide
  should present it as an adoptable pattern, not as validated incident reduction.

### Claim 9: Automated analysis of completed traces should flag anomalous sessions for human review, so humans review flags rather than every session
- **Evidence**: The author describes automated analysis over duration, cost, tool
  count, loop detection, and token efficiency, with loops/high cost/tool errors
  flagged for humans; the stated volume problem is hundreds of sessions daily.
- **Confidence**: emerging
- **Quote**: "Humans review the flags, not every session."
- **Our assessment**: This is a sensible answer to the review-capacity problem and
  a direct application of sampling-by-exception: cheap automated checks run on
  every completed trace, expensive human attention is allocated to flagged ones.
  It also creates a feedback loop for tuning the flags. The article does not
  define the flagging thresholds or measure precision/recall, so the pattern is
  sound but the classifier is unspecified.

### Claim 10: Export only bounded metrics to Prometheus — tool success/failure by tool name, per-agent session cost, approval latency histograms, classification counts — as a complement to traces
- **Evidence**: The article enumerates the metric set explicitly and states that
  bounded metrics are for real-time dashboards and alerting; traces remain the
  debugging substrate.
- **Confidence**: emerging
- **Quote**: "For real-time dashboards and alerting, export bounded metrics to Prometheus (or similar): tool success/failure rates by tool name, per-agent session costs, approval latency histograms, classification counts."
- **Our assessment**: The boundedness criterion is the important design rule:
  every listed dimension (tool name, agent name) has a small finite value set,
  which is what makes the metric set safe to aggregate and alert on. Approval
  latency is an agent-specific signal the corpus's observability notes do not
  emphasize — stale approvals are a blocked-agent failure mode that looks like
  slowness, not error. The article gives the set, not the query/alert rules.

### Claim 11: Never put unique identifiers such as session IDs in Prometheus labels; thousands of daily sessions will cause a cardinality explosion that crashes the metrics server
- **Evidence**: The cardinality warning is stated as a production constraint, with
  the safe/unsafe split made explicit: tool names and agent names are bounded and
  safe; unique identifiers are not, and per-session detail belongs in the tracing
  backend or structured logs.
- **Confidence**: emerging (the underlying Prometheus cardinality behavior is
  settled; the "crashes the metrics server" outcome is asserted from experience)
- **Quote**: "Never put unique identifiers like session IDs into Prometheus labels. A production system running thousands of agent sessions daily will cause a cardinality explosion that crashes the metrics server."
- **Our assessment**: A concrete, testable operational constraint and one of the
  genuinely additive pieces relative to the tracing-focused notes. It is the
  agent-specific instance of a general rule (the telemetry-pipeline note makes
  the same argument for `user_id`/`request_id`), and the Langfuse Metrics API
  encodes the same restriction by refusing high-cardinality grouping dimensions.
  The fix is architectural: per-session detail lives in traces/logs; metrics carry
  only bounded dimensions.

### Claim 12: Cost is the primary canary — sudden cost spikes almost always indicate a bug, so alert on cost first and debug second
- **Evidence**: The author's "Lessons Learned" list states the rule and names the
  three bug classes behind most spikes: loops, model routing errors, and
  unbounded context accumulation.
- **Confidence**: emerging
- **Quote**: "Sudden cost spikes almost always indicate a bug — loops, model routing errors, or unbounded context accumulation. Alert on cost first, debug second."
- **Our assessment**: The causal ordering is the interesting claim: cost is not
  just a budget signal, it is an early *correctness* signal because the common
  failure modes are expensive. "Almost always" is an unsupported frequency claim
  and should not be quoted as a rate; the useful guidance is to make cost a
  first-class alert dimension alongside latency and errors, which the vendor
  observability notes also recommend.

### Claim 13: Traces are for debugging and metrics are for alerting — do not alert on traces (too detailed) or debug with metrics (too aggregated)
- **Evidence**: Stated as an explicit division of labor in "Lessons Learned,"
  immediately after the bounded-metrics section.
- **Confidence**: emerging
- **Quote**: "Don't try to alert on traces (too detailed) or debug with metrics (too aggregated). Use both."
- **Our assessment**: A crisp restatement of the trace/metrics split that the
  corpus's observability material already implies (Honeycomb's traces, Datadog's
  operational dashboards, Langfuse's metric layer). It is sharper than most
  sources about the *reason* — alerting needs a low-cardinality, pre-aggregated
  signal; debugging needs the full per-session detail — and it is consistent with
  the article's own automated trace analysis (Claim 9), which is post-hoc
  analysis, not alerting on traces.

### Claim 14: Audit-log PII redaction is non-negotiable because the audit trail will be queried during incident reviews
- **Evidence**: The author's fourth lesson: an audit trail containing credentials
  or PII turns the observability tool into a liability; tool outputs with
  sensitive data must be sanitized before logging.
- **Confidence**: emerging
- **Quote**: "If it contains credentials or PII, your observability tool becomes a liability."
- **Our assessment**: Correct and important: the audit trail's evidentiary value
  is exactly what makes it a high-value breach target, and incident review is the
  moment of maximum exposure. The article states the requirement (sanitize before
  logging) but gives no redaction mechanism, so it complements rather than
  duplicates the corpus's concrete vendor redaction tooling. This belongs in the
  security chapter as a hard rule for agent I/O logging.

## Concrete Artifacts

### Artifact 1: The three agent observability pillars

From the "The Three Pillars for Agents" section:

```
1. Traces — The Session Timeline
   agent trace = full decision history (model calls, tool invocations,
   sub-agent delegations) with timing and cost attached; sub-agent work
   nests as child spans.

2. Costs — The Unit Economics Question
   per session: total cost, token breakdown, which model did what
   per agent over time: daily burn rate, session count, cost trends

3. Audit — The Immutable Record
   every tool call, governance decision, memory operation →
   append-only, structured, timestamped, searchable; sensitive tool
   outputs sanitized before logging.
```

### Artifact 2: "What to Watch" signal table (verbatim)

From the "What to Watch" section:

| Signal | Why it matters |
|---|---|
| Session cost vs rolling average | Catches loops and runaway context early |
| Identical consecutive tool calls | Loop detection before cost explodes |
| Approval latency | Stale approvals mean blocked agents |
| Model error rate | Provider issues vs agent bugs |
| Vector store/integration health | Silent dependency failures |
| Daily token burn vs budget | Invoice surprises |
| Audit log growth rate | Potential runaway execution |

### Artifact 3: Pre-flight guardrails vs reactive alerting

Extracted from the "Costs — The Unit Economics Question" and
"Lessons Learned" sections:

```
Pre-flight (first line of defense, inside the request path):
  - hard iteration caps
  - per-tool call budgets
  - loop detection that blocks identical consecutive calls

Reactive (second line of defense):
  - alert when a single session exceeds a multiple of the
    rolling average cost for that agent
  - rationale: a tight loop in a parallel agent can burn budget
    in seconds, before a webhook fires

Debugging substrate:
  - agent traces (per-session full decision history)
Alerting substrate:
  - bounded Prometheus metrics (tool success/failure by tool name,
    per-agent session cost, approval latency histograms,
    classification counts)
```

### Artifact 4: Doctor-style diagnostic command scope (verbatim list)

From "The Diagnostic Command" section:

```
- model connectivity
- vector store reachability
- pending approvals
- memory counts
- trace backend status
- integration health
```

### Artifact 5: Automated session-review flags (from "Automated Session Reviews")

```
Analysis dimensions on completed traces:
  duration, cost, tool count, loop detection, token efficiency flags

Flagged for human review:
  loops, high cost, tool errors
```

## Cross-References

- **Corroborates**:
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claim 1** ("The LLM is rarely the root cause of agent failures"), **Claim
    2** (the three required attributes `gen_ai.conversation.id`,
    `gen_ai.agent.name`, `gen_ai.operation.name`), and **Claim 3** ("a 'GenAI
    span' is not just an LLM call"). Honeycomb supplies the OpenTelemetry
    attribute-level contract for the session trace this post describes
    structurally; both put tool calls, downstream work, and sub-agent handoffs
    inside the debugging surface. This post adds the cost and audit layers above
    that trace model.
  - `source-notes/docs-langfuse-metrics-overview.md` **Claim 6** ("Dimensions like
    id, traceId, userId, and sessionId cannot be used for grouping in the v2
    Metrics API" / "Grouping by these high cardinality fields is extremely
    expensive and rarely useful in practice"). This is an independent
    implementation-level confirmation of this post's Claim 11: Langfuse enforces
    at the API what the post warns about for Prometheus labels. Two different
    vendors/layers converging on the same cardinality rule is strong support that
    session IDs belong outside the aggregated metrics surface.
  - `source-notes/blog-cncf-telemetry-that-matters-observability-pipelines.md`
    **Claim 8** (high-cardinality management: "Avoid attaching highly unique
    attributes like user_id or request_id directly to system metrics, which can
    instantly trigger a dimensional explosion that breaks backend query engines")
    and **Claim 12** (agentic systems need observability beyond latency/error rates,
    including "semantic prompt/response patterns" and "decision quality"). The
    cardinality argument is the same rule with different examples; Claim 12's
    "decision quality" framing is the broader version of this post's "did the
    agent actually do what it said it did?" question.
  - `source-notes/docs-datadog-llm-observability.md` **Claim 5** (out-of-the-box
    operational dashboards monitor "the cost, latency, performance, and usage
    trends for all your LLM applications"), **Claim 9** (evaluations associated
    with individual spans so the inputs/outputs that produced an eval are
    visible), and **Claim 10** (Sensitive Data Scanner scans and redacts sensitive
    input/output). Datadog independently treats cost as a first-class operational
    dimension and PII redaction as a pipeline requirement — the same two pillars
    this post argues for from production experience.
  - `source-notes/docs-langfuse-alerts.md` **Claim 1** (alerts can be driven by
    observation-level operational metrics such as `avg latency`, `count`,
    `p95 cost` or by score metrics) and **Claim 2** (a warning-then-alert
    two-threshold ladder over a time window). This post specifies *what* to alert
    on (session cost vs rolling average) and *why* (cost as canary); the Langfuse
    note documents a shipped mechanism for expressing precisely that kind of
    metric threshold alert. The article's ordering caveat still applies: these
    are the second line of defense behind pre-flight caps.
  - `source-notes/docs-google-sre-prodcast-01-03-alerting.md` **Claim 13**
    ("generalized anomaly detection for alerting doesn't generally work...
    anomalies— they are likely to just lead to wild goose chases and be a
    distraction"). This post's cost alert is a *curated* metric with a relative
    threshold (a multiple of the rolling average for a named agent), not a
    blanket anomaly detector — so it is consistent with the Google guidance
    rather than an exception to it. The guide should present it that way: choose
    the signal and the threshold deliberately; do not infer "alert on any
    anomaly" from this claim.
  - `source-notes/blog-pagerduty-production-ai-agent-gaps.md` **Claim 12** (a
    metrics framework tracking task success, tool error rates, loop and retry
    rate, p95 latency, cost per successful task, safety violations, and human
    escalation rate). PagerDuty's production metrics set overlaps this post's
    "what to watch" signals (tool errors, loops, cost) and adds quality/outcome
    dimensions. Both argue that agent monitoring must extend beyond request
    health.

- **Contradicts**: None identified. The only apparent friction is internal and
  resolves as a conditioning variable: Claim 13 says don't alert on traces, while
  Claim 9 uses automated analysis of completed traces — but Claim 9 is post-hoc
  flagging, not synchronous alerting, and Claim 10 keeps alerting on bounded
  metrics. No contradiction issue filed.

- **Extends**:
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` —
    Honeycomb answers "what do I put on the spans?" (attributes, naming, error
    propagation, PII handling for prompt/response capture). This post answers
    "what do I do with the resulting telemetry?" — cost accounting per session,
    an append-only audit trail, alerting on bounded metrics, cardinality
    discipline, and automated session triage. The two are complementary layers of
    one agent-observability stack.
  - `source-notes/blog-cncf-jaeger-ai-agent-tracing-opentelemetry.md` — Jaeger
    describes the tracing backend/query direction (Claims 1, 9, 12); this post
    describes the operator practices above any trace backend, explicitly naming
    Langfuse as the backend in use. It adds the cost/audit/alerting layer the
    Jaeger roadmap does not cover.
  - `source-notes/docs-litellm-a2a-iteration-budgets.md` — LiteLLM documents
    **gateway-level** per-session caps: **Claim 1** (`max_iterations` hard cap on
    LLM calls per session and `max_budget_per_session` dollar cap), **Claim 2**
    (the caps are fail-open unless the outbound trace-id flag is set), **Claim 4**
    (budget is checked before each call and accumulated after each successful one,
    so it rejects one call late), and **Claim 6** (counters are TTL-windowed at
    1 hour, so "per session" is really "per rolling hour"). This post describes
    **application-level** pre-flight breakers — iteration caps, per-tool budgets,
    identical-consecutive-call loop detection — as the first line of defense.
    Together they give the guide two enforcement loci for the same class of
    control, plus the LiteLLM note's caveats about fail-open defaults and
    windowing that an app-level implementation must also address.
  - `source-notes/blog-cncf-network-boundary-ai-agents-nginx-otel.md` **Claim 3**
    (the NGINX OpenTelemetry module emits an OTel span per outbound request, and
    an OTel Collector can persist those spans to an audit log or SIEM). That note
    provides a network-boundary audit plane for agent egress; this post specifies
    the audit *record* semantics (append-only, includes governance decisions and
    memory operations, sanitize sensitive tool outputs before logging). The two
    loci are complementary: network spans show what left the boundary; the
    application audit log records what the agent decided and remembered.

- **Novel** (relative to the corpus):
  - The explicit **ordering rule** that pre-flight loop/cost guardrails are the
    first line of defense and alerting is second, justified by webhook latency
    versus the burn rate of a parallel loop (Claim 5).
  - **Cost-vs-rolling-average per agent** as the named anomaly alert condition,
    with the three slow-burn failure classes it targets (Claim 6).
  - The **Prometheus cardinality rule for agent session IDs** stated as a
    production crashing constraint (Claim 11), with the safe/unsafe label split
    (tool/agent names safe; unique IDs not).
  - A **doctor-style one-shot agent dependency diagnostic** with a concrete
    check list (Claim 8).
  - **Automated session review by exception** — automated flags for loops/high
    cost/tool errors, humans review only the flags (Claim 9).
  - An **append-only agent audit record** that includes governance decisions and
    memory operations, with sanitize-before-logging as the rule (Claims 7, 14).

## Guide Impact

- **Chapter 02 (Observability)**: Add the three-pillar agent model (traces for
  debugging, bounded metrics for alerting, append-only audit for reconstruction)
  as the organizing frame for agent observability, citing Claims 2, 7, 10, 13.
  Add the cardinality rule (Claim 11) as a hard constraint: never put session IDs
  or other unique identifiers in metric labels; keep per-session detail in the
  tracing backend or structured logs. The current chapter's trace/metrics
  material should point at this as the agent-specific specialization, and the
  bounded metric set in Claim 10 (tool success by name, per-agent session cost,
  approval latency, classification counts) is a ready-to-adopt starting list.

- **Chapter 05 (LLM Ops Reliability)**: Add the pre-flight-before-alert ordering
  (Claim 5) as a reliability rule for agent loops: hard iteration caps, per-tool
  call budgets, and identical-consecutive-call loop detection belong in the
  request path; cost alerting is the second line of defense. Add the
  cost-vs-rolling-average alert (Claim 6) as a concrete canary for
  hallucination spirals, routing errors, and context accumulation, with the
  caveat that the multiplier and rolling window are unspecified and must be
  tuned per agent. Add the automated-completed-trace review pattern (Claim 9) as
  the triage layer: analyze every trace cheaply, flag anomalies, spend human
  attention only on flags.

- **Chapter 03 (Runbooks and Agents)**: Add the doctor-style diagnostic command
  (Claim 8) as a first-run/triage runbook step for agent operators, with the
  concrete dependency list (model connectivity, vector store, pending approvals,
  memory counts, trace backend, integration health). Pair it with Claim 3's
  non-blocking export rule as the telemetry-side runbook check: an unreachable
  trace backend should degrade telemetry, not the agent.

- **Chapter 04 (Oncall and Toil)**: Use Claim 9 to make manual review of every
  session an explicit anti-pattern: at hundreds of sessions per day, review is
  by exception. Use Claim 10's approval-latency signal as an on-call signal for
  blocked agents (stale approvals are a queueing failure that does not look like
  an error). Use Claim 2's per-agent cost trend as the context an on-call needs
  to judge whether a cost alert is a loop or a traffic change.

- **Chapter 06 (Security and Trust)**: Add the append-only agent audit record
  (Claim 7) with the three event classes (tool calls, governance decisions,
  memory operations) and the hard rule that sensitive tool outputs are sanitized
  before logging (Claim 14). Frame it as an evidentiary record whose value during
  incident review is exactly why it must not contain credentials or PII.

## Extraction Notes

- **Related-notes candidates reviewed** (all ten from `miner-related-notes.md`,
  each cited or explicitly dismissed):
  - `docs-google-sre-prodcast-03-07-retail-gaming.md` — **dismissed**: SLO/
    gaming/retail operations; no agent tracing, cost, audit, or cardinality
    content.
  - `blog-cncf-cloud-native-agentic-ai-security-platform.md` — **dismissed**: its
    pre-LLM Isolation Forest gate (Claim 5) and OPA/Kyverno policy-as-code
    (Claim 3) are security controls, not cost/loop guardrails; no shared claim
    with this post.
  - `docs-google-sre-eliminating-toil.md` — **dismissed**: toil taxonomy and
    measurement; the connection to "review flags, not every session" is a
    synthesis, not a claim in either source.
  - `docs-google-sre-prodcast-03-01.md` — **dismissed**: SRE methodology and
    feedback cycles; no agent-observability specifics.
  - `docs-litellm-anthropic-advisor-tool.md` — **dismissed**: within-request
    model composition and advisor billing semantics; unrelated.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — **dismissed**:
    change-workflow paradigms; unrelated.
  - `docs-google-sre-reliable-product-launches.md` — **dismissed**: launch
    coordination/checklists; no overlap with continuous agent session review.
  - `docs-google-sre-on-call.md` — **dismissed**: on-call staffing, pager load,
    alerting hygiene; it does not address reviewing completed agent traces or
    per-session cost alerts.
  - `docs-google-sre-prodcast-03-06-incident-response-tooling.md` — **dismissed**:
    incident tooling and paging topology; no agent telemetry content.
  - `docs-google-sre-prodcast-03-09-profiling-data.md` — **dismissed**: profiling
    data modalities and clustering; unrelated to agent session cost/audit.
- **Additional notes reviewed** (beyond the candidate list, found by searching
  `source-notes/` and cross-checking the Prospector's named overlaps):
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`,
  `blog-cncf-jaeger-ai-agent-tracing-opentelemetry.md`,
  `docs-datadog-llm-observability.md`, `docs-langfuse-metrics-overview.md`,
  `docs-langfuse-alerts.md`, `docs-google-sre-prodcast-01-03-alerting.md`,
  `blog-cncf-telemetry-that-matters-observability-pipelines.md`,
  `docs-litellm-a2a-iteration-budgets.md`,
  `blog-cncf-network-boundary-ai-agents-nginx-otel.md`, and
  `blog-pagerduty-production-ai-agent-gaps.md`. Also checked and **dismissed**:
  `blog-cncf-opencost-inference-cost-tracking.md` (GPU allocation-vs-usage
  economics for self-hosted inference, a different cost layer) and
  `blog-cncf-cloud-native-agentic-ai-security-platform.md` (security policy
  gating, as above).
- **Quote verification**: All `Quote` fields are contiguous strings copied from
  the fetched source page. Where the rendered text carries markdown emphasis
  (e.g. "**agent trace**", "**pre-flight circuit breakers**"), the quote records
  the visible words without the formatting markers. The "What to Watch" table
  (Artifact 2) is transcribed cell-for-cell from the source table.
- **No contradiction issue filed**: The apparent tension between "don't alert on
  traces" (Claim 13) and "automated analysis on completed traces" (Claim 9) is a
  post-hoc-vs-synchronous distinction, not a disagreement about the same system.
  Likewise, the cost-vs-rolling-average alert is a curated threshold, not the
  generalized anomaly detection the Google alerting note warns against. Per
  MINER.md §4a these are conditioning variables, recorded in Cross-References
  rather than filed as contradictions.
- **Confidence note**: `confidence_overall` is `emerging`. The source is a
  practitioner report from months of production operation, but it presents no
  incident data, no before/after metrics, no benchmark numbers, and no concrete
  alert parameters (multiplier, window, cap values). Every claim is recorded as
  pattern guidance, not validated result.
- **Deep-read scope**: The article is self-contained and short; no substantive
  linked pages were followed. The Langfuse docs it names are already represented
  in the corpus by `docs-langfuse-metrics-overview.md` and
  `docs-langfuse-alerts.md`, so those notes were used for cross-reference instead
  of re-fetching the vendor site.
