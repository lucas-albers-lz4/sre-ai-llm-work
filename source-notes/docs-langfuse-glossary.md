---
source_url: https://langfuse.com/docs/glossary
source_type: docs
title: "Glossary — Langfuse"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: "unknown (Langfuse vendor docs; page footer © 2022–2026)"
date_extracted: 2026-07-15
last_checked: 2026-07-15
status: current
confidence_overall: settled
issue: "#255"
---

# Glossary — Langfuse

> A 57-term reference glossary for the Langfuse platform. Low pattern/evidence
> density (per triage), but it is the first place in our corpus that lays out
> two definitional structures whole: the **observation-type taxonomy** (Agent,
> Chain, Embedding, Event, Generation, Guardrail, Retriever, Span, Tool,
> Evaluator) and the **trace → observation → session** data-model hierarchy that
> the deeper Langfuse notes (#195, #196, #131) assume but never define.

## Source Context

- **Type**: docs (vendor reference / terminology page)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor documenting its own product vocabulary; term definitions are
  authoritative and factual (settled) rather than opinion. The page's "Last
  edited" contributor is Jannik Maierhöfer; footer © 2022–2026 Langfuse GmbH /
  Finto Technologies Inc.
- **Scope**: Defines 57 terms across six filterable categories — Observability,
  Evaluation, Prompts, SDK, Platform, API. Each entry is a 1–3 sentence
  definition plus a "Related:" cross-link list. It contains **no code, config,
  metrics, or failure detail** — it is a navigation/terminology aid, not a
  narrative article. Pricing terms (Billable Unit) are out of the seed's scope
  and not extracted as guide-relevant.
- **Relationship to existing notes**: This is the fourth Langfuse docs note.
  The three deeper siblings already extract the *mechanics* — evaluation loop and
  Score model (#195), Datasets and versioning (#196), MCP servers (#131). This
  note deliberately does **not** re-extract those; it captures only the
  definitional scaffolding those notes lean on plus a handful of terms none of
  them touch (observation types, prompt-management vocabulary, RBAC/platform
  model, Remote Experiment, Langfuse Assistant, Filter Search Bar).

## Extracted Claims

### Claim 1: Langfuse's telemetry data model is a three-level hierarchy — a Trace is one request/operation, containing nested Observations (individual steps), and Traces are grouped into Sessions (a user interaction)
- **Evidence**: The `Trace`, `Observation`, and `Session` glossary entries,
  read together, define the containment hierarchy the deeper Langfuse notes
  assume without stating.
- **Confidence**: settled
- **Quote**: "A single request or operation in your LLM application. Traces contain the overall input, output, and metadata, along with nested observations that capture each step."
- **Our assessment**: This is the load-bearing structural definition missing from
  our corpus. The evaluation note (#195, Claim 3) says a Score attaches to "a
  trace, an observation, a session, or a dataset run" but never defines what
  those four objects *are* or how they nest. This glossary supplies that:
  Session ⊃ Trace ⊃ Observation. Genuinely useful as the one-paragraph
  orientation the guide needs before it can talk about attaching evals at the
  right granularity.

### Claim 2: An Observation is typed, and Langfuse enumerates a fixed taxonomy of observation types — Span, Generation, Event, Tool, Agent, Chain, Embedding, Retriever, Guardrail, Evaluator
- **Evidence**: The `Observation` entry states observations "can be of different
  types," and ten separate glossary entries are each tagged "(Observation Type)"
  with a distinct definition.
- **Confidence**: settled
- **Quote**: "An individual step within a trace. Observations can be of different types (span, generation, event, tool, etc.) and can be nested to represent hierarchical workflows."
- **Our assessment**: This typed-observation taxonomy is entirely new to the
  corpus and is the single most extractable structure on the page (see Concrete
  Artifacts for the full table). It matters because it is the vocabulary an SRE
  uses to *read a trace*: a failure is localized to a Tool observation vs a
  Generation vs a Retriever. This directly complements Honeycomb's OTel-span
  framing (Claim 3 there: "A GenAI span is any span in the agent's execution
  chain, not just LLM calls") — Langfuse gives those spans named semantic types.

### Claim 3: Span is the default observation type ("duration of a unit of work"); Generation is the LLM-call type that logs prompts, completions, token usage and costs
- **Evidence**: The `Span` and `Generation` glossary entries.
- **Confidence**: settled
- **Quote**: "An observation type that logs outputs from AI models including prompts, completions, token usage, and costs. The most common observation type for LLM calls."
- **Our assessment**: The Span-vs-Generation distinction is the practical core of
  the taxonomy: Span = generic timed work, Generation = model call with
  cost/token accounting. This is where Langfuse's cost/latency attribution hangs
  (Model Definition, Token entries). Aligns with Honeycomb Claim 3's "GenAI span
  is any span" — both separate the LLM call from the surrounding orchestration
  steps.

### Claim 4: Guardrail is a first-class observation type representing a component that protects against malicious content, jailbreaks, or other security risks
- **Evidence**: The `Guardrail (Observation Type)` glossary entry.
- **Confidence**: settled
- **Quote**: "An observation type that represents a component protecting against malicious content, jailbreaks, or other security risks."
- **Our assessment**: Notable that safety controls are modeled as a *traced*
  observation type, not an out-of-band concern — a guardrail invocation shows up
  in the trace alongside the Generation it protects, so an SRE can see whether a
  guardrail fired. Small but genuinely new to the corpus and directly relevant to
  the Ch06 security thread (agent input/output safety being observable).

### Claim 5: A Score is the output of any annotation or automated evaluation, is one of four types (numeric, categorical, boolean, text), and attaches to traces, observations, sessions, or dataset runs
- **Evidence**: The `Score` glossary entry.
- **Confidence**: settled
- **Quote**: "The output of an annotation or automated evaluation. Scores can be numeric, categorical, boolean, or text and are assigned to traces, observations, sessions, or dataset runs."
- **Our assessment**: This is a terse restatement of the Score data model already
  extracted at depth in #195 (Claim 2–3). It **corroborates** that note exactly —
  same four types, same four attachment targets — which is a useful independent
  confirmation that the deeper note read the model correctly. No new mechanism;
  cite #195 for the full treatment.

### Claim 6: Langfuse defines an "AI Engineering Loop" — a lifecycle connecting production visibility to development via tracing → datasets → experiments → evaluation, then repeating
- **Evidence**: The `AI Engineering Loop` glossary entry (tagged both
  Observability and Evaluation).
- **Confidence**: emerging
- **Quote**: "A lifecycle for continuously improving AI-powered systems by connecting production visibility with development workflows. It moves from tracing and monitoring real behavior to building datasets, running experiments, and evaluating changes before the cycle starts again."
- **Our assessment**: This is the named/branded version of the offline→online
  closed loop that #195 (Claim 1) extracts in full with a worked chatbot example.
  The glossary reduces it to one sentence — not enough depth to stand alone, but
  it confirms the loop is a first-class Langfuse concept with a name, not just an
  incidental description. Extends #195, adds no new mechanism. Marked emerging
  (like #195 Claim 1) since it is vendor framing of a still-consolidating pattern.

### Claim 7: Langfuse is built on OpenTelemetry, which it presents as reducing vendor lock-in
- **Evidence**: The `OpenTelemetry (OTel)` glossary entry (tagged Observability
  and SDK).
- **Confidence**: settled
- **Quote**: "An open standard for collecting telemetry data from applications. Langfuse is built on OpenTelemetry, enabling interoperability and reducing vendor lock-in."
- **Our assessment**: An architecturally important one-liner absent from the
  three prior Langfuse notes: the platform sits on OTel, so the observation model
  above (Claims 1–3) is an OTel-span model with LLM-specific semantic types. This
  is the connective tissue to the Honeycomb OTel-GenAI-conventions note — Langfuse
  and Honeycomb describe the *same* underlying span standard from the app-platform
  vs observability-backend ends. Worth a Ch02 cross-reference.

### Claim 8: Prompt Management is a distinct product concern — storing/versioning/retrieving prompts to decouple prompt updates from code deployment — with a Prompt Label mechanism to mark versions (e.g. production/staging) fetched by SDK/API
- **Evidence**: The `Prompt Management`, `Prompt Label`, `Chat Prompt`,
  `Text Prompt`, and `Prompt Variables` glossary entries.
- **Confidence**: settled
- **Quote**: "A systematic approach to storing, versioning, and retrieving prompts for LLM applications. Decouples prompt updates from code deployment."
- **Our assessment**: Prompt management is a category none of the three prior
  Langfuse notes cover — they are all evaluation/MCP focused. The "decouple prompt
  updates from code deployment" framing is the load-bearing idea: prompts become a
  versioned, labeled artifact you can roll forward/back independently of a code
  deploy — the prompt-side analogue of the versioned golden dataset in #196
  (Claim 4). Genuinely novel to the corpus; flagged for a future dedicated
  prompt-management source.

### Claim 9: Protected Prompt Labels restrict who can move sensitive labels (e.g. production) onto new prompt versions, limiting that to admins/owners to prevent accidental or unauthorized production changes
- **Evidence**: The `Protected Prompt Label` glossary entry.
- **Confidence**: settled
- **Quote**: "Restricts the ability to modify certain prompt labels (e.g. production) from being added to new prompt versions to admins and owners. This prevents accidental or unauthorized changes to production prompts."
- **Our assessment**: This is a change-management / blast-radius control for
  prompts — the same "who can promote to production" governance SREs apply to
  deploys, applied to prompt versions. New to the corpus and relevant to Ch06
  (access control) and any chapter treating prompts as production artifacts.

### Claim 10: Langfuse's access model is a three-tier RBAC hierarchy — Organization (billing/SSO/members) ⊃ Project (data + fine-grained RBAC) ⊃ API Key (public+secret, project-scoped) — with roles Owner, Admin, Member, Viewer, None
- **Evidence**: The `Organization`, `Project`, `RBAC`, and `API Key` glossary
  entries read together.
- **Confidence**: settled
- **Quote**: "Role-Based Access Control that manages permissions within Langfuse. Roles include Owner, Admin, Member, Viewer, and None, each with specific scopes."
- **Our assessment**: The MCP note (#131, Claim 8) states each API key is
  "project-scoped" but never defines the surrounding Org/Project/RBAC model. This
  glossary supplies it: the project scope that bounds an MCP key's blast radius is
  one level of a three-tier hierarchy. Useful Ch06 context — it explains exactly
  what an authenticated MCP key can and cannot reach.

### Claim 11: Remote Experiment is a webhook-triggered mechanism to run SDK experiments from the Langfuse UI — the UI calls a webhook that fetches the dataset, runs the app, and ingests scores back
- **Evidence**: The `Remote Experiment` glossary entry.
- **Confidence**: settled
- **Quote**: "A webhook-based trigger that allows running SDK experiments from the Langfuse UI. Configure a webhook URL and default config, then trigger experiments that fetch the dataset, run your application, and ingest scores back into Langfuse."
- **Our assessment**: A concrete integration primitive absent from #195/#196,
  which describe SDK-run and UI-run experiments (evaluation note Claim 8) but not
  this hybrid: UI-initiated, webhook-dispatched to your own runner, scores
  ingested back. This is the "run my CI/eval harness from a button in the UI"
  bridge and worth recording so the eval-harness chapter (Ch05) knows the UI can
  drive an external runner, not only the SDK.

### Claim 12: Langfuse Assistant is a beta in-product AI agent that answers plain-language questions over project data by querying traces/observations/sessions/metrics through the Langfuse MCP server
- **Evidence**: The `Langfuse Assistant` glossary entry.
- **Confidence**: settled
- **Quote**: "An in-product AI assistant, available in beta on Langfuse Cloud, for exploring project data and Langfuse workflows in plain language. It queries traces, observations, sessions, and metrics through the Langfuse MCP server, searches documentation, and proposes navigation actions that you confirm."
- **Our assessment**: A concrete consumer of the authenticated MCP data-platform
  server documented in #131 (Claim 8): the vendor's own first-party agent uses its
  own MCP surface to read project data. Note the human-in-the-loop guardrail —
  it "proposes navigation actions that you confirm" rather than acting
  autonomously. Extends #131 with a worked example of who calls that MCP server.

### Claim 13: The Filter Search Bar lets users query the Observations/Traces tables via field:value expressions (with operators, wildcards, negation) and an "Ask AI" button that drafts filters from plain language
- **Evidence**: The `Filter Search Bar` glossary entry.
- **Confidence**: settled
- **Quote**: "A single-line query bar for filtering and searching the Observations and Traces tables by typing field:value expressions instead of assembling filters in the sidebar. Supports operators, wildcards, negation, and an Ask AI button that drafts filters from a plain-language description."
- **Our assessment**: A minor UI feature, but the "Ask AI drafts a filter from
  natural language" detail is a small instance of the recurring theme in this
  corpus — LLMs embedded into the observability tooling itself (cf. Langfuse
  Assistant, Claim 12). Low priority; recorded for completeness.

## Concrete Artifacts

The page contains no code, config, or metrics. Its one extractable structure is
the observation-type taxonomy, reproduced verbatim below (each definition copied
from its glossary entry).

### Observation-type taxonomy (verbatim definitions from the glossary)
```
Type       | Category      | Definition (verbatim)
-----------+---------------+---------------------------------------------------------------
Span       | Observability | An observation type that represents the duration of a unit of
           |               | work in a trace. The default observation type for most operations.
Generation | Observability | An observation type that logs outputs from AI models including
           |               | prompts, completions, token usage, and costs. The most common
           |               | observation type for LLM calls.
Event      | Observability | A basic observation type used to track discrete events in a
           |               | trace. Events are the building blocks of tracing.
Tool       | Observability | An observation type that represents a tool call in your
           |               | application, such as calling a weather API or executing a
           |               | database query.
Agent      | Observability | An observation type that represents an AI agent workflow,
           |               | including multi-step reasoning processes, tool orchestration,
           |               | and autonomous decision-making. Used to track agent behavior
           |               | and interactions.
Chain      | Observability | An observation type that represents a link between different
           |               | application steps, such as passing context from a retriever
           |               | to an LLM call.
Embedding  | Observability | An observation type that represents a call to an LLM to generate
           |               | embeddings. Can include model information, token usage, and costs.
Retriever  | Observability | An observation type that represents data retrieval steps, such
           |               | as calls to vector stores or databases in RAG applications.
Guardrail  | Observability | An observation type that represents a component protecting
           |               | against malicious content, jailbreaks, or other security risks.
Evaluator  | Observability | An observation type that represents functions assessing the
           |               | relevance, correctness, or helpfulness of LLM outputs. Also
           |               | refers to the function that scores experiment results.
```
Source: langfuse.com/docs/glossary (each row is that term's full glossary
definition, character-for-character). The category column reflects the page's
own "Observability" filter tag on every one of these entries.

### The trace/observation/session containment hierarchy (composed from three verbatim entries)
```
Session   "A way to group related traces that are part of the same user interaction.
           Commonly used for multi-turn conversations or chat threads."
  └─ Trace "A single request or operation in your LLM application. Traces contain the
            overall input, output, and metadata, along with nested observations that
            capture each step."
       └─ Observation "An individual step within a trace. Observations can be of different
                       types (span, generation, event, tool, etc.) and can be nested to
                       represent hierarchical workflows."
```
Note: the nesting arrows are our composition; the quoted definitions are verbatim
from the individual `Session`, `Trace`, and `Observation` glossary entries. The
containment direction is stated by each entry (a Session groups Traces; a Trace
contains nested Observations).

## Cross-References

- **Corroborates**:
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 3** — the Score
    data model. The glossary `Score` entry (this note, Claim 5) restates it
    verbatim in miniature: same four types (numeric/categorical/boolean/text) and
    same four attachment targets (traces, observations, sessions, dataset runs).
    Independent confirmation that #195 read the model correctly; no new mechanism.
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 1** — the
    offline→online evaluation loop. The glossary `AI Engineering Loop` entry
    (this note, Claim 6) is the one-sentence named version of the same lifecycle
    #195 walks with a worked example.
- **Extends**:
  - `docs-langfuse-datasets.md` (#196) **Claim 1** (a Dataset is a collection of
    inputs + expected outputs) — the glossary `Dataset`, `Dataset Item`, and
    `Dataset Experiment` entries give the terse definitional forms, and add the
    `Task` term (the app function under test) and `Remote Experiment` (this note,
    Claim 11), a UI→webhook experiment trigger not covered in #196.
  - `docs-langfuse-mcp-server.md` (#131) **Claim 8** (authenticated,
    project-scoped MCP data server). The glossary supplies (a) the surrounding
    RBAC/Org/Project model that defines what "project-scoped" bounds (this note,
    Claim 10) and (b) a first-party consumer of that MCP server — `Langfuse
    Assistant` (this note, Claim 12).
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 3** ("A
    GenAI span is any span in the agent's execution chain, not just LLM calls").
    The glossary's OpenTelemetry entry (this note, Claim 7 — "Langfuse is built on
    OpenTelemetry") plus the observation-type taxonomy (Claim 2) are the
    app-platform-side naming of the same OTel spans Honeycomb describes from the
    backend side.
- **Novel** (not present in the corpus before this note):
  - The **observation-type taxonomy** — ten named, semantically-typed observation
    kinds (Claim 2, full table in Concrete Artifacts). None of #195/#196/#131
    define observation types.
  - The **Session ⊃ Trace ⊃ Observation** containment hierarchy stated explicitly
    (Claim 1).
  - **Guardrail as a traced observation type** (Claim 4).
  - The **prompt-management vocabulary** — Prompt Management, Prompt Label,
    Protected Prompt Label, Chat/Text Prompt, Prompt Variables (Claims 8–9). A
    product area untouched by the three prior Langfuse notes.
  - The **Organization/Project/RBAC/API-Key access hierarchy** with named roles
    (Claim 10).
  - **Remote Experiment** (UI→webhook experiment trigger, Claim 11) and
    **Langfuse Assistant** (Claim 12) and **Filter Search Bar / Ask AI**
    (Claim 13).
- **Contradicts**: None. Every overlapping definition is consistent with the
  deeper notes (the `Score` entry matches #195 Claim 3 exactly; `Dataset` matches
  #196 Claim 1; `MCP Server` matches #131). No contradiction issue filed.

## Guide Impact

- **Chapter 02 (Observability)**: Add a short "Langfuse data model" orientation
  box drawn from Claims 1–3: Session ⊃ Trace ⊃ Observation, and the typed-
  observation taxonomy (Span/Generation/Tool/Retriever/Guardrail/Agent/…). This
  is the vocabulary a reader needs *before* the deeper eval/dataset material in
  #195/#196 makes sense — e.g., #195's "attach a Score to an observation" only
  lands once "observation" is defined. Pair with the OpenTelemetry note (Claim 7)
  and the Honeycomb OTel-conventions note so the guide presents one span model
  named from both the app-platform (Langfuse types) and backend (OTel GenAI
  conventions) sides. Evidence: Claims 1, 2, 3, 7.
- **Chapter 05 (LLM Ops Reliability — eval harness)**: One-line addition only —
  record `Remote Experiment` (Claim 11) as the UI-initiated, webhook-dispatched
  way to run an external eval runner from Langfuse, complementing the SDK-run and
  UI-run experiment paths already covered by #195 (Claim 8). Also note the named
  "AI Engineering Loop" (Claim 6) as Langfuse's branded term for the loop #195
  already documents — no re-extraction needed.
- **Chapter 06 (Security and Trust)**: Two concrete additions. (1) The RBAC/
  Org/Project/API-Key hierarchy (Claim 10) defines exactly what an authenticated
  MCP key's "project scope" (from #131 Claim 8) bounds — cite it when discussing
  MCP blast radius. (2) Protected Prompt Labels (Claim 9) are a prompt-side
  change-management control (only admins/owners can promote to `production`) worth
  citing alongside deploy-gating governance. Guardrail-as-observation (Claim 4)
  is a minor supporting point: safety controls are traceable, not out-of-band.
- **Not recommended**: Do not treat this page as evidence for any pattern's
  *value* — it is definitional. Cite it only for vocabulary/orientation and for
  the genuinely new terms (observation types, prompt-management vocabulary, RBAC
  model). Prefer the deeper siblings (#195/#196/#131) for mechanism and the
  practitioner notes (PagerDuty, Honeycomb) for evidence.

## Extraction Notes

- Source fetched 2026-07-15. WebFetch returned empty for this page (JS-heavy
  Next.js render, identical behavior to the sibling `docs-langfuse-*.md` notes),
  so the page was retrieved with `curl` and readable text extracted from the HTML
  (`<script>`/`<style>`/`<svg>`/`<noscript>` stripped, tags removed, HTML
  entities decoded). All 57 terms rendered server-side and were fully readable;
  every quote in this note is copied character-for-character from that extracted
  prose, which matches the page's displayed definitions.
- The page self-reports "Showing 57 of 57 terms" across six filter categories
  (Observability, Evaluation, Prompts, SDK, Platform, API). I read all 57. This
  note extracts the subset that is (a) genuinely new to the corpus or (b) the
  definitional scaffolding the deeper Langfuse notes assume. Terms already
  extracted at depth elsewhere (Dataset/Dataset Item/Dataset Experiment/Task in
  #196; Evaluation Method/LLM-as-a-Judge/Offline+Online Evaluation/Annotation
  Queue/Score Config in #195; MCP Server/Public API in #131) are referenced in
  Cross-References rather than re-extracted. Pure-vendor/pricing/UI-plumbing terms
  (Billable Unit, Custom Dashboards, Metrics API, Model Definition, Token, Token
  Tracking, Tags, User Tracking, Log View, Flush, Instrumentation, SDK, LLM
  Connection, Playground, Environment) are noted but not promoted to claims —
  they carry no guide-actionable content beyond definition. `Environment` and
  `Model Definition` are mentioned in-line where relevant.
- The three Prospector triage comments all rated novelty **low** ("no code,
  config, metrics, or failure details — just brief 1–2 sentence descriptions").
  That read is respected and reflected in the framing: this note foregrounds the
  small amount of genuinely novel definitional structure (observation-type
  taxonomy, prompt-management vocabulary, RBAC model) and explicitly declines to
  re-extract what the deeper siblings already cover. `confidence_overall` is
  **settled** because glossary definitions of a shipped product are factual and
  authoritative; the *value* of the underlying patterns is established (or not)
  by the deeper notes and practitioner sources, not here.
- No part of the source was paywalled; the glossary is fully public. No
  contradiction with existing notes surfaced (the overlapping definitions match
  the deeper notes exactly), so no contradiction issue was filed.
