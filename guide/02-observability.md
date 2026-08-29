# Observability

> Instrumenting LLM-powered applications — the span/trace model for agent
> workloads, the observability spectrum, wiring SLOs to drill-down data, and
> keeping the human in the debugging loop.

## The observability model for LLM applications

### One trace per request

An LLM application request is represented as a single trace you can monitor,
troubleshoot, and evaluate. A trace takes one of three shapes, forming a
maturity ladder for instrumentation
[source: docs-datadog-llm-observability, Claim 1, Claim 2] [emerging]:

1. **Single LLM inference** — one LLM span with tokens, errors, latency.
2. **Predetermined workflow** — root workflow span + nested LLM/tool/preprocessing
   spans in a fixed sequence.
3. **Dynamic agent** — root agent span + nested workflows, LLM calls, and tool
   calls with no predetermined order.

This ladder explains why naive "just trace the LLM call" coverage is
insufficient for agents — the workflow and agent tiers require grouping
surrounding operations (tool calls, retrieval, handoffs).

**Rule**: Scope your instrumentation to the highest tier your application
reaches. If your system is an agent, tracing only the LLM call misses the
tool calls, retrievals, and handoffs where most failures live.

### The seven-kind span taxonomy

Spans are categorized by the type of work they perform
[source: docs-datadog-llm-observability, Claim 4] [settled]:

| Kind | What it represents | Can be root? |
|------|-------------------|--------------|
| LLM | A call to a model | Yes |
| Workflow | A predetermined sequence of operations | Yes |
| Agent | A series of autonomous decisions/operations | Yes |
| Tool | A call to a program/service (args from LLM) | No |
| Task | A standalone step (no external call) | No |
| Embedding | A call returning an embedding | No |
| Retrieval | A data retrieval from external knowledge base | No |

A span carries: name, start time/duration, error info, inputs and outputs
(prompts and completions), metadata (model params like `temperature`), and
metrics (`input_tokens`, `output_tokens`)
[source: docs-datadog-llm-observability, Claim 3] [settled].

**Rule**: Instrument every LLM call, tool call, and retrieval as a distinct
span kind. The Tool and Retrieval spans are where agentic failures
concentrate — tracing them separately from the LLM span is what makes those
failures debuggable.

### Two vendors, one standard: OTel GenAI semantic conventions

Datadog natively ingests OpenTelemetry GenAI semantic convention v1.37+
spans without requiring the Datadog SDK
[source: docs-datadog-llm-observability, Claim 12] [settled].

Honeycomb's instrumentation aligns with the same operation model
(`gen_ai.operation.name`: chat, execute_tool, retrieval, embeddings,
invoke_agent, invoke_workflow)
[source: blog-honeycomb-instrumenting-ai-agents-opentelemetry, Concrete Artifacts]
[emerging]. Two independently-authored vendor docs converge on the same
operation taxonomy.

**Rule**: Standardize on the OTel GenAI semantic-convention operation and
attribute model. It is the vendor-neutral schema that at least two major
observability vendors consume natively.

### Auto-instrumentation covers the framework layer; application context is manual

Framework auto-instrumentation traces supported LLM libraries without code
changes, but it cannot infer your conversation boundaries, agent identity, or
custom business spans. Those require manual instrumentation
[source: docs-datadog-llm-observability, Claim 11] [emerging].

**Rule**: Auto-instrumentation handles the LLM/framework call layer. You must
manually propagate conversation ID, agent identity, and custom span context
through your application code.

## Observability as a spectrum

### From monitoring to on-demand analysis

Observability is a spectrum, not a binary — basic monitoring (logs + metrics)
is a low degree of observability; on-demand analysis of tracing and
structured-log data is more complete coverage
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 2]
[emerging]:

```
No observability  →  you can't see anything
Limited (OBS 1.0) →  logs + metrics for the questions you anticipated
More complete      →  on-demand analysis of traces + structured logs
  (OBS 2.0)           for questions you didn't anticipate
```

Pre-aggregated metrics can only answer questions you thought to ask in
advance. High-cardinality trace and structured-log data lets you ask new
questions after the fact — which is what debugging an agent's unexpected
behavior requires.

**Rule**: Define capabilities, not labels. Ask "how far along the spectrum
are we?" not "do we have observability?" The term has been diluted — vendors
rename APM to observability the same way orgs renamed sysadmins to DevOps
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 3]
[anecdotal].

### Observability serves the human's mental model

Debugging is the scientific method: form a mental model of how the system
functions, ask a falsifiable question, decide what to measure, interpret the
results. An image means nothing until a person interprets it
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 5]
[settled].

This is the intellectual core of why the human stays in the loop:
observability is not the dashboard — it is the hypothesis → test → refine
cycle that a human runs.

**Rule**: Observability tooling should help humans form and test hypotheses,
not replace their judgment. The dashboard answers questions; it doesn't know
which questions to ask.

## Wiring SLOs to drill-down data

### SLOs without drill-down are a dead end

An SLO signal ("user transactions are exceeding 3,000 milliseconds") must be
backed by a distributed trace or structured log so you can bisect the problem
to the implicated component and user population
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 9]
[settled].

> Don't put AIOps on top of cause-based alerts when the trace data to drill
> down already exists. Wire your SLOs to that ability to drill down and
> investigate.

The anti-pattern: bolting AI onto alert triage when the fix is better
instrumentation. You already have the data if you're doing tracing.

**Rule**: Every user-facing SLO must reference a trace or structured log that
lets you follow the transaction end-to-end and bisect to the failing
component. If your SLO burns and you can't drill down, the SLO itself is
broken.

### Topic clustering of production traffic

Datadog Patterns automatically clusters LLM production traffic into a topic
hierarchy using self-hosted open-source embeddings + UMAP + HDBSCAN, without
manual tagging. Each topic shows interaction volume, cost, tokens, errors,
and latency [source: docs-datadog-llm-observability, Claim 6, Claim 7]
[emerging].

The pipeline: pull interactions → summarize with AI → embed with open-source
model → cluster with UMAP + HDBSCAN → generate topic names → build hierarchy.
Caps at 10,000 records per run; 5-10 minute background runtime.

**Rule**: Cluster your production LLM traffic by topic to find eval-coverage
gaps and failure-mode concentrations. The topic with unexpectedly high error
rate relative to volume is your next eval target. Unclustered traffic (the
"Outliers" group) is itself a signal.

### Anomaly detection dimensions for LLM apps

Detect regressions across three dimensions: span name, workflow type, and
topic clusters. Analyze over the past week
[source: docs-datadog-llm-observability, Claim 8] [emerging].

**Rule**: Anomaly detection for LLM apps should watch span-level, workflow-level,
and topic-cluster-level signals. A single aggregate error rate hides the
regression.

## SLI measurement design

Two first-party SLO-adoption journeys supply the design rules for *how* to
measure an SLI — directly transferable to LLM service SLIs.

### Evernote: external prober, two-location "down", maintenance as downtime

Evernote measured availability with an external third-party prober
(Pingdom) that was "located completely outside of and independent from our
environment so we could test all our components, including our load
balancing stack." A node was marked down for SLO purposes only after a
second geographically separate prober confirmed the first failure, and
maintenance windows were treated as downtime: "Uninformed users would
therefore experience these windows as generic and unexplained downtime"
[source: docs-google-sre-slo-engineering-case-studies, Claim 4] [settled].

**Rule**: Measure user-experienced availability from outside the stack,
require multi-location confirmation before declaring an outage, and count
announced maintenance as downtime — your users' experience, not your
operational announcements, defines the SLI.

### THD: percentiles, 5xx-only errors, no utilization

THD's SLI rules: latency as percentiles over arithmetic averages ("at
minimum, services needed to hit a 90th percentile target; user-facing
services had a preferred target of 95th and/or 99th percentile"), a
black-box supplement to white-box monitoring, error classification
standardized on HTTP codes with SLOs set on 5xx only (4xx tracked but
excluded), and an explicit decision against utilization SLOs — "your users
don't really care about utilization as long as you can handle the traffic
volume" [source: docs-google-sre-slo-engineering-case-studies, Claim 9,
Claim 10] [settled].

**Rule**: Latency SLIs are percentiles, not averages; error SLOs count
service-side (5xx) failures with client errors still tracked; and leave
utilization out of the user-facing SLO.

## Batch-pipeline health signals

LLM data work (eval refresh, embedding backfills, index rebuilds) is batch
work, and batch health is a different signal shape than request health.

### Freshness as the primary batch health metric

A batch pipeline's health is measured by freshness — "time since the last
successful completion of the job" — and a job that overruns its schedule is a
paging event, mitigated by an on-call rotation before the freshness SLO is
violated [source: docs-google-sre-reliable-data-processing-minimal-toil,
Claim 15] [settled].

**Rule**: Every batch pipeline needs a freshness SLO and a schedule-overrun
alert. The silent failure mode of a data pipeline is not an error — it is a
job that quietly stops completing on time [source:
docs-google-sre-reliable-data-processing-minimal-toil, Claim 15] [settled].

### The two-phase mutation as a continuous health monitor

The two-phase mutation pattern — stage candidate IDs, validate them
separately, apply only after validation passes — can run continuously in
production as a health monitor, not just during changes [source:
docs-google-sre-reliable-data-processing-minimal-toil, Claim 12] [settled].

**Rule**: Run your data-validation pass as a standing production monitor, so
corruption that would break a backfill is caught by a health check rather
than by the next scheduled run [source:
docs-google-sre-reliable-data-processing-minimal-toil, Claim 12] [settled].

## AI-assisted observability

### AI as copilot, not driver

Machine/AI assistance in observability should help humans refine their mental
model — never be the primary driver. Outsourcing system understanding to
automation leads to model divergence (the "737 MAX" problem): people think
the system is doing one thing and don't actually understand it because the
models have diverged
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 10]
[emerging].

Honeycomb's BubbleUp is an example: the user draws a box around an anomaly;
the AI surfaces correlated changes and suggests follow-up questions but never
asserts causation ("maybe it's causation, maybe it's correlation, the AI
doesn't really know").

**Rule**: AI in observability should guide humans to better questions, not
replace their understanding. A system that answers "what changed?" is a
copilot; a system that asserts "this caused that" has overstepped.

### If SREs lose hands-on exposure, they lose the safety margin

If SREs do not have exposure to their systems, they drift away from knowing
the limits of those systems. Knowing your safety margin — and knowing when
you've lost it — requires hands-on contact
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 11]
[settled].

**Rule**: Automate genuine toil and abstract away other teams' problems, but
keep hands-on exposure to the systems you own. On-call time should include
exploring production to build a mental baseline, so during an incident you
can distinguish real problems from cosmetic ones
[source: docs-google-sre-prodcast-03-04-observability-spectrum, Claim 12]
[emerging].

## Scripting the observability data plane

Observability vendors expose the data plane to automation, not just the UI and
SDKs. Langfuse's CLI wraps the entire API — traces, observations, prompts,
datasets, scores, sessions, metrics — generated from the OpenAPI spec so every
endpoint is a command [source: docs-langfuse-cli, Claim 2] [settled], and it
authenticates with the same project API-key pair as the SDKs via environment
variables, with no separate login step [source: docs-langfuse-cli, Claim 4]
[settled]. The stated scripting use cases are agent-managed data operations and
CI/CD automation: "exporting traces, batch-scoring, or syncing prompts across
environments in CI/CD or bash scripts" [source: docs-langfuse-cli, Claim 6]
[settled].

**Rule**: Script your telemetry data plane — batch exports, re-scoring, and
cross-environment prompt sync should be CLI-automatable with the same env-var
credentials as the SDKs, not locked behind the UI.

## Platform-side observability: shared SLO dashboards

For any platform with tenants, observability extends across the
platform/tenant boundary. Google's platform-SRE doctrine: audit the
customer's monitoring and build shared dashboards. "Up to half of the things
your customer is measuring (and alerting on) have zero impact on their SLOs" —
the remaining measurements are candidate SLIs, uncovered SLO dimensions need
new measurements, and the goal is a shared SLO dashboard so that whenever a
customer contacts you because their SLO seems threatened, "you shouldn't have
to swap much additional information" [source:
docs-google-sre-reaching-beyond-walls, Claim 8] [settled].

This is the observability corollary of "your users, not your monitoring,
decide your reliability": "your monitoring, logs, and alerting are valuable
only insofar as they help you notice problems before your customers do"
[source: docs-google-sre-reaching-beyond-walls, Claim 2] [settled].

**Rule**: For an LLM platform, audit tenant telemetry against tenant
quality/latency/cost SLIs and build a shared SLO dashboard. Much of what
tenants alert on (token counts, generic p95) may not track their stated app
SLOs — turn off the SLO-irrelevant alerting on both sides.

The failure mode a shared dashboard exists to prevent: a provider's global
SLO rollup can hide region-isolated outages for a small-footprint tenant.
Because Evernote's VM footprint was "only a small percentage of the global
GCP number," outages isolated to its region could be lost in the overall
rollup to a global level even while the provider's graphs stayed green —
which is why Evernote shared real-time SLO dashboards with the provider's
CRE team, received SLO-impact-quantified notifications ("this issue is
causing a 5% impact to Evernote's SLO"), and treated high-SLO-impact
incidents as mutual P1s on a shared bridge [source:
docs-google-sre-slo-engineering-case-studies, Claim 6] [settled].

**Rule**: For an LLM platform, a global model-quality SLO can mask a region-
or tenant-specific degradation. Share tenant-scoped SLO dashboards and
quantify impact in the tenant's terms — the aggregate number will not show
it.

---
*Sources for this chapter: docs-datadog-llm-observability,
docs-google-sre-prodcast-03-04-observability-spectrum,
blog-honeycomb-instrumenting-ai-agents-opentelemetry,
docs-google-sre-reliable-data-processing-minimal-toil,
docs-google-sre-reaching-beyond-walls,
docs-google-sre-slo-engineering-case-studies, docs-langfuse-cli*
*Last updated: 2026-08-29*
