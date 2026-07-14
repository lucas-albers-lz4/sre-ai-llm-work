---
source_url: https://langfuse.com/docs/evaluation/core-concepts
source_type: docs
title: "Langfuse Evaluation — Core Concepts"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; current as of 2026-07-14)
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: emerging
issue: "#195"
---

# Langfuse Evaluation — Core Concepts

> A vendor reference for the evaluation architecture of a production LLM
> observability platform: the offline→online evaluation loop, the Score data
> model that unifies all eval results, a five-method evaluation taxonomy, and
> the experiment workflow (dataset → task → evaluation → scores → iteration).
> Provides the concrete, tool-level instantiation of the eval-loop discipline
> the guide currently discusses only abstractly.

## Source Context

- **Type**: documentation (vendor product docs — Langfuse evaluation subsystem)
- **Author credibility**: Langfuse is a widely-used open-source LLM observability
  platform (tracing, prompt management, evaluation). The "Core Concepts" page is
  the conceptual overview for its evaluation product; sub-pages ("Scores",
  "LLM-as-a-Judge", "Experiments"/"Datasets") detail the implementation. The
  claims describe how the product is *designed to be used*, so they are
  authoritative for the tool's intended patterns but are vendor-authored and not
  independently benchmarked. Credibility is raised by convergence with an
  independent practitioner account (PagerDuty, see Cross-References).
- **Scope**: Covers (1) the evaluation loop (offline vs online), (2) the Score
  data model (types + what objects scores attach to), (3) the evaluation-method
  taxonomy and when each applies, (4) experiments (datasets, tasks, runs,
  iteration), (5) online evaluation of production traces, (6) SDK/UI code
  patterns for datasets and experiments. Does NOT cover: pricing, self-hosting
  ops, security/guardrails specifics, or model-selection guidance.
- **Sub-pages followed**: To satisfy the triage's "concrete code/config
  snippets" requirement, I followed three linked pages: the **Datasets /
  Experiments** page (`/docs/evaluation/experiments`) for SDK code
  (`create_dataset`, `create_dataset_item`, `run_experiment`, JSON-Schema
  validation), and the **LLM-as-a-Judge** page (`/docs/evaluation/evaluation-methods`)
  for the judge-prompt structure and the observation/trace/experiment targeting
  model. The dedicated "Scores" page (`/docs/evaluation/scores`) is
  client-rendered and returned no static body, so score-creation code is not
  quoted; the score *data model* is fully covered by the Core Concepts page
  itself.

## Extracted Claims

### Claim 1: Evaluation is a closed loop — offline evaluation tests against a fixed dataset before deploy; online evaluation scores live traces, and edge cases found online are fed back into the dataset
- **Evidence**: Core Concepts "The Evaluation Loop" section plus the worked
  chatbot example. The page explicitly frames LLM apps as having "a constant
  loop of testing and monitoring" and walks a tone-change scenario where a
  French-language query caught in production is added to the dataset so future
  experiments catch it.
- **Confidence**: emerging
- **Quote**: "Offline evaluation lets you test your application against a fixed dataset before you deploy." / "Online evaluation scores live traces to catch issues in real traffic. When you find edge cases your dataset didn't cover, you add them back to your dataset so future experiments will catch them."
- **Our assessment**: This is the highest-value pattern in the source and the
  reason the Prospector flagged it. The loop — offline experiment → deploy →
  online monitor → edge-case → dataset growth → offline catches it next time —
  is exactly the eval discipline the guide references abstractly (golden
  datasets + CI gates). Langfuse supplies a concrete, tool-backed realization.
  Corroborated independently by PagerDuty's golden-dataset + LLM-as-a-judge +
  CI-gate pipeline (see Cross-References).

### Claim 2: Scores are Langfuse's universal data object for any evaluation result — whether from a human, an LLM judge, a programmatic check, or end-user feedback, the result is stored as a score
- **Evidence**: Core Concepts "Scores" section. The abstraction is presented as
  the unifying primitive of the whole evaluation subsystem.
- **Confidence**: settled (within Langfuse's model)
- **Quote**: "Scores are Langfuse's universal data object for storing evaluation results. Any time you want to assign a quality judgment to an LLM output, whether by a human annotation, an LLM judge, a programmatic check, or end-user feedback, the result is stored as a score."
- **Our assessment**: A clean unifying abstraction — every eval source funnels
  into one object type, which makes analytics, dashboards, and comparison uniform
  regardless of how the score was produced. Complementary to the OpenTelemetry
  `gen_ai.evaluation.result` span-event pattern (Honeycomb note, Claim 11):
  Langfuse stores the same eval result as a first-class object, not only as a
  span event. See Cross-References.

### Claim 3: Every Score has a name, a value, and one of four data types — NUMERIC, CATEGORICAL, BOOLEAN, or TEXT — and can be attached to a trace, an observation, a session, or a dataset run
- **Evidence**: Core Concepts "Scores" section; the LLM-as-a-Judge page adds
  concrete guidance on which type to use (numeric for continuous 0–1 judgments
  like helpfulness, categorical for explicit labels like correct/incorrect,
  boolean for binary policy/scope decisions).
- **Confidence**: settled
- **Quote**: "Scores can be attached to traces, observations, sessions, or dataset runs. Every score has a name, a value, and a data type (NUMERIC, CATEGORICAL, BOOLEAN, or TEXT)."
- **Our assessment**: The four-type model plus multi-level attachment is the
  key design point. Granularity matters: a score can live at the whole-trace
  level, at an individual observation (a single LLM/retrieval/tool call), at a
  session, or at a dataset run — so eval results can be as coarse or as precise
  as the question being asked. This is the first explicit score data model in
  our corpus.

### Claim 4: Langfuse's evaluation-method taxonomy has five methods, each with a defined "use when" condition — LLM-as-a-Judge, Code evaluators, Scores via UI, Annotation Queues, Scores via API/SDK
- **Evidence**: Core Concepts "Evaluation Methods" table.
- **Confidence**: settled
- **Quote**: (verbatim table rows) "LLM-as-a-Judge — Use an LLM to evaluate outputs based on custom criteria — Subjective assessments at scale (tone, accuracy, helpfulness)" / "Code evaluators — Run custom Python or TypeScript logic to score observations or experiments — Deterministic checks, structured output validation, custom business rules" / "Scores via UI — Manually add scores to traces directly in the Langfuse UI — Quick quality spot checks, reviewing individual traces" / "Annotation Queues — Structured human review workflows with customizable queues — Building ground truth, systematic labeling, team collaboration" / "Scores via API/SDK — Programmatically add scores using the Langfuse API or SDK — Custom evaluation pipelines, deterministic checks, automated workflows"
- **Our assessment**: The taxonomy cleanly separates four concerns: subjective
  (LLM-judge), deterministic (code), one-off human (UI), systematic human
  (annotation queue), and programmatic pipeline (API/SDK). Useful as a menu for
  teams standing up an eval harness — pick by the "use when," not by fashion.

### Claim 5: LLM-as-a-Judge uses a judge model to score another LLM's output against a rubric; a typical judge prompt contains evaluation criteria (a rubric), input context, output to evaluate, and an optional reference/ground truth
- **Evidence**: LLM-as-a-Judge sub-page — definition and the "A typical
  LLM-as-a-Judge prompt includes" list.
- **Confidence**: emerging
- **Quote**: "LLM-as-a-Judge is an evaluation methodology where an LLM is used to assess the quality of outputs produced by another LLM application." / "A typical LLM-as-a-Judge prompt includes: Evaluation criteria — a rubric defining what 'good' looks like ... Input context — the original user query or prompt ... Output to evaluate — the application's response ... Optional reference — ground truth or expected output for comparison"
- **Our assessment**: The canonical four-part judge-prompt structure
  (criteria / input / output / reference) is actionable and matches how
  PagerDuty's pipeline uses an LLM-as-a-judge to compare actual vs expected
  output. The rubric is the load-bearing part — without a defined "what good
  looks like," the judge score is noise.

### Claim 6: LLM-as-a-Judge can target three levels — Observations (individual operations, recommended for production), Traces (whole workflows, legacy), and Experiments (offline datasets) — and the production pattern is to validate with Experiments in dev, then deploy Observation-level evaluators in production
- **Evidence**: LLM-as-a-Judge sub-page "Decision Tree" and "Production
  Pattern". The page argues Observation-level evaluators are dramatically faster
  (seconds, thousands per minute, asynchronous), give operation-level precision,
  and allow compositional evaluation (toxicity on outputs, relevance on
  retrievals, accuracy on generations simultaneously).
- **Confidence**: emerging
- **Quote**: "Production Pattern: Teams typically use Experiments during development to validate changes, then deploy Observation-level evaluators in production for scalable, precise monitoring."
- **Our assessment**: The Observations-first recommendation is the most
  operationally useful guidance in the source for Ch05. Running judges on every
  whole trace is slow and expensive; scoping the judge to the specific
  observation (e.g., the final LLM response) cuts volume and cost while keeping
  precision. This is a concrete scaling pattern, not just a feature list.

### Claim 7: An experiment runs an application task against a dataset and scores the outputs; the building blocks are Dataset, Dataset item (input + optional expected output), Task (the app code under test), Evaluation Method, Score, and Experiment Run
- **Evidence**: Core Concepts "Experiments → Definitions" and "How these work
  together."
- **Confidence**: settled
- **Quote**: "An experiment runs your application against a dataset and evaluates the outputs. This is how you test changes before deploying to production."
- **Our assessment**: This is the structured offline-testing workflow —
  dataset → task → evaluation → scores → compare runs → deploy decision. It maps
  one-to-one onto PagerDuty's golden-dataset + CI-gate pattern (Claim 10): the
  "task" is the agent under test, the "evaluation method" is the LLM-as-a-judge,
  and comparing experiment runs is the gate. Langfuse supplies the data model and
  UI for it.

### Claim 8: Experiments can be run two ways — programmatically via the SDK (full control of task + evaluation logic) or via the UI by selecting a dataset and prompt version (quick prompt iteration without code)
- **Evidence**: Core Concepts "Two ways to run experiments."
- **Confidence**: settled
- **Quote**: "You can run experiments programmatically using the Langfuse SDK. This gives you full control over the task, evaluation logic, and more." / "Another way is to run experiments directly from the Langfuse interface by selecting a dataset and prompt version. This is useful for quick iterations on prompts without writing code."
- **Our assessment**: The SDK/UI split mirrors the dev-vs-quick-iteration
  distinction. The SDK path is the one that integrates into CI gates
  (PagerDuty Claim 10); the UI path is for prompt-tuning velocity. Both share the
  same underlying dataset, which the source recommends managing in Langfuse for
  in-UI comparison tables and iterative improvement from production traces.

### Claim 9: Datasets can be versioned (timestamped) and experiments run against a pinned dataset version, enabling reproducibility — re-running historical versions, comparing before/after dataset changes, and testing against a fixed baseline
- **Evidence**: Experiments/Datasets sub-page `run_experiment` SDK code plus the
  versioning explanation. The Python SDK fetches a dataset at a specific
  `version` timestamp and runs `run_experiment` against that frozen state.
- **Confidence**: emerging
- **Quote**: "This approach ensures reproducibility by allowing you to: Re-run experiments on historical dataset versions even after items are updated or deleted ... Compare model performance before and after dataset changes ... Maintain experiment consistency and reproduce exact results from previous runs"
- **Our assessment**: Dataset versioning is the reproducibility backbone of any
  deploy-gating eval harness. Without it, "the eval passed" is not reproducible
  and you cannot attribute a score change to the model/prompt vs the test data.
  High value for Ch05 — the guide should treat the golden dataset as a
  versioned, reviewed artifact, not a loose folder of examples.

### Claim 10: Datasets support optional JSON-Schema validation on input and expectedOutput so all items conform to a defined structure, catching malformed items early and keeping test data consistent across a team
- **Evidence**: Experiments/Datasets sub-page "Schema Enforcement" section and
  the `create_dataset(input_schema=...)` SDK example.
- **Confidence**: emerging
- **Quote**: "Optionally add JSON Schema validation to your datasets to ensure all dataset items conform to a defined structure. This helps maintain data quality, catch errors early, and ensure consistency across your team."
- **Our assessment**: Treating eval datasets as schema-validated, tested
  artifacts elevates them from ad-hoc examples to reliable test fixtures. This
  dovetails with the curated-SLI / golden-dataset discipline noted in the
  alerting source (Claim 13): a dataset is only as trustworthy as its curation,
  and validation is one enforcement mechanism.

### Claim 11: Online evaluation auto-scores production traces (via LLM-as-a-Judge, code evaluators, or human annotation) to catch issues immediately, and Langfuse provides real-time dashboards to monitor scores
- **Evidence**: Core Concepts "Online Evaluation" and "Monitoring with
  dashboards" sections.
- **Confidence**: emerging
- **Quote**: "For online evaluation, you can configure evaluation methods to automatically score production traces. This helps you catch issues immediately."
- **Our assessment**: This is the production half of the closed loop (Claim 1).
  Combined with the feedback step (edge cases → dataset), online evaluation is
  what keeps the eval set representative as real traffic evolves. Ties directly
  into Ch02 observability — eval scores become monitorable signals alongside
  latency and tokens.

## Concrete Artifacts

### The Evaluation Loop (from Core Concepts — "The Evaluation Loop")

```
                 ┌─────────────────────────────────────────────┐
   DEPLOY ───────►  ONLINE                                        │
                   Trace: traces · sessions · agents · prompts    │
                   Monitor: dashboards · LLM-as-judge · feedback  │
                        │                                         │
                        ▼  edge cases found online ──┐            │
                 ┌──────────────────────────────┐   │            │
                 │  OFFLINE                       │   │            │
                 │  Build:   datasets · features  │   │            │
                 │  Experiment: prompts · models  │   │            │
                 │  Evaluate:  judges · custom    │   │            │
                 └──────────────────────────────┘   │            │
                         ▲                            │            │
                         └──── add to dataset ◄───────┘            │
                              (so future experiments catch them)  │
                              └───────────────────────────────────┘
```
> Source: langfuse.com/docs/evaluation/core-concepts — the page renders this as
> a Deploy → Online → Offline cycle; reconstructed as an ASCII flow.

### Worked example — the closed loop on a customer-support chatbot (verbatim narrative beats from Core Concepts)

1. "You update your prompt to make responses less formal."
2. "Before deploying, you run an experiment: test the new prompt against your dataset of customer questions (offline evaluation)."
3. "You review the scores and outputs. The tone improved, but responses are longer and some miss important links."
4. "You refine the prompt and run the experiment again. The results look good now. You deploy the new prompt to production."
5. "You monitor with online evaluation to catch any new edge cases."
6. "You notice that a customer asked a question in French, but the bot responded in English."
7. "You add this French query to your dataset so future experiments will catch this issue."
8. "You update your prompt to support French responses and run another experiment."
9. "Over time, your dataset grows from a couple of examples to a diverse, representative set of real-world test cases."

### Evaluation Methods table (verbatim from Core Concepts)

```
Method             | What                                                         | Use when
-------------------+--------------------------------------------------------------+-------------------------------------------------------------
LLM-as-a-Judge     | Use an LLM to evaluate outputs based on custom criteria      | Subjective assessments at scale (tone, accuracy, helpfulness)
Code evaluators    | Run custom Python or TypeScript logic to score observations  | Deterministic checks, structured output validation,
                    | or experiments                                               | custom business rules
Scores via UI      | Manually add scores to traces directly in the Langfuse UI    | Quick quality spot checks, reviewing individual traces
Annotation Queues  | Structured human review workflows with customizable queues    | Building ground truth, systematic labeling, team collaboration
Scores via API/SDK | Programmatically add scores using the Langfuse API or SDK   | Custom evaluation pipelines, deterministic checks,
                                                                                 | automated workflows
```

### SDK: create a dataset (Python, verbatim from Experiments/Datasets page)

```python
langfuse.create_dataset(
    name = "<dataset_name>",
    # optional description
    description = "My first dataset",
    # optional metadata
    metadata = {
        "author" : "Alice",
        "date" : "2022-01-01",
        "type" : "benchmark"
    }
)
```

### SDK: add a dataset item with input + expected output (Python, verbatim)

```python
langfuse.create_dataset_item(
    dataset_name = "<dataset_name>",
    # any python object or value, optional
    input = {
        "text" : "hello world"
    },
    # any python object or value, optional
    expected_output = {
        "text" : "hello world"
    },
    # metadata, optional
    metadata = {
        "model" : "llama3",
    }
)
```

### SDK: run an experiment against a versioned dataset (Python, verbatim)

```python
from langfuse import Langfuse
langfuse = Langfuse()
version_timestamp = datetime(2025, 12, 15, 6, 30, 0, tzinfo = timezone.utc)
# Fetch versioned dataset
versioned_dataset = langfuse.get_dataset("qa-dataset", version = version_timestamp)
# Run experiment on the versioned dataset
def my_llm_application(*, item, **kwargs):
    # Your LLM application logic here
    # For this example, we'll just return the expected output
    return item.expected_output
result = versioned_dataset.run_experiment(
    name = "Baseline Experiment v1",
    description = "Running on dataset v1",
    task = my_llm_application
)
```

### SDK: enforce a JSON Schema on a dataset (Python, verbatim, truncated at expected_output)

```python
langfuse.create_dataset(
    name = "qa-conversations",
    input_schema = {
        "type" : "object",
        "properties" : {
            "messages" : {
                "type" : "array",
                "items" : {
                    "type" : "object",
                    "properties" : {
                        "role" : { "type" : "string", "enum" : ["user", "assistant", "system"]},
                        "content" : { "type" : "string" }
                    },
                    "required" : ["role", "content"]
                }
            }
        },
        "required" : ["messages"]
    },
    expected_outpu...   # (truncated in source extraction)
)
```

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 10** ("Automated
    evaluation pipelines using golden datasets + LLM-as-a-judge + CI gates are
    essential for production-grade agent systems"). Langfuse provides the
    systematic, tool-level instantiation of the *same* loop: offline Experiments
    = the golden dataset + CI gate; the LLM-as-a-Judge evaluation method = the
    judge step; online evaluation = the production-monitoring half. Not a
    contradiction — Langfuse goes deeper on the data model and the
    closed-loop/dataset-growth mechanics. Both also agree the judge needs a
    defined rubric/expected output (**Claim 5** here ↔ PagerDuty's
    "LLM-as-a-judge is then used to compare the agent's actual output against
    the expected output").
  - `docs-google-sre-prodcast-01-03-alerting.md` **Claim 13** ("generalized
    anomaly detection for alerting does not generally work… alert on curated
    SLIs") and its Cross-cutting synthesis #3 ("Agent 'anomaly' alerts need
    curated SLIs… exactly the evaluation discipline the existing AI notes
    advocate"). Langfuse's eval loop is a concrete implementation of that
    curated-SLI discipline: scores are curated, dataset-defined quality signals
    (not raw anomalies), and Claim 10's JSON-Schema validation is one way to
    enforce dataset curation. Directionally aligned, not in tension.

- **Extends**:
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 11**
    ("Evaluation results should be attached as span events to GenAI operation
    spans" — the `gen_ai.evaluation.result` attribute). Complementary layering
    rather than overlap: Langfuse stores eval results as a universal **Score**
    object attached across trace / observation / session / dataset-run (this
    note, **Claim 2–3**), while Honeycomb attaches the same eval result as a
    span event on the GenAI operation span for cost/latency/quality correlation
    in one query. Together they describe the eval-result data model at two
    layers — the app/eval platform (Langfuse) and the observability backend
    (Honeycomb/OTel GenAI conventions). The guide should present both: store
    scores as first-class objects *and* emit them as span events.

- **Novel** (first appearances in the corpus):
  - First **Langfuse** reference in any source note or guide chapter.
  - First explicit **Score data model** — four typed kinds (NUMERIC /
    CATEGORICAL / BOOLEAN / TEXT) with multi-level attachment (trace /
    observation / session / dataset run).
  - First **evaluation-method taxonomy** with explicit "use when" conditions
    (LLM-as-a-Judge / Code / UI / Annotation Queue / API-SDK).
  - First **dataset-versioning-for-reproducibility** pattern as the backbone of
    a deploy-gating eval harness (**Claim 9**).
  - First concrete **closed-loop feedback mechanic** stated as a product pattern:
    online edge cases → dataset growth → future offline experiments catch them
    (**Claim 1**).

- **Contradicts**: None identified. All overlapping notes are complementary
  (confirmed by the Prospector triage and by re-reading the cited claims). No
  contradiction issue filed.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — currently a stub)**: This source is the
  strongest concrete material for the eval-harness topic the chapter targets.
  Specific additions:
  - The **offline→online closed-loop eval pattern** (Claim 1) as the recommended
    shape of an eval discipline: dataset → experiment → deploy → online monitor
    → edge-case → dataset growth. Frame it as the operational realization of the
    abstract "golden dataset + CI gate" advice already in the AI notes.
  - The **Score data model** (Claim 2–3) as the recommended way to store *all*
    eval results uniformly (human, LLM-judge, programmatic, end-user feedback)
    and to attach them at the right granularity (observation-level for
    production scaling per Claim 6).
  - The **evaluation-method taxonomy** (Claim 4) as a "pick by use-when" menu
    for teams building a harness.
  - **Dataset versioning for reproducibility** (Claim 9) as a hard requirement
    for any deploy-gating eval: the golden dataset must be a versioned, reviewed
    artifact, not a loose folder. Add **JSON-Schema validation** (Claim 10) as
    the enforcement mechanism.
  - **Observation-level online eval** (Claim 6) as the production scaling
    pattern — judges on individual operations, not whole traces.

- **Chapter 02 (Observability — annotation pipelines)**: Extend the
  observability story with the human-in-the-loop pieces:
  - **Annotation Queues + UI scoring** (Claim 4) as the structured human-review
    / ground-truth-building pipeline — distinct from automated scoring.
  - **Scores attached to traces/observations/sessions** (Claim 3) as
    monitorable quality signals alongside latency and tokens.
  - **Online evaluation + dashboards** (Claim 11) as the live quality-monitoring
    layer that closes the loop with offline experiments.
  - Cross-reference the Honeycomb `gen_ai.evaluation.result` span-event pattern
    (Claim 11 there) so Ch02 presents eval results at both layers: stored as
    Langfuse Scores *and* emitted as OTel span events.

## Extraction Notes

- Source is a Next.js docs site. The Core Concepts page rendered server-side and
  was fully readable via curl + HTML-strip. The **Datasets/Experiments** and
  **LLM-as-a-Judge** sub-pages also rendered server-side and supplied the
  concrete SDK code and the judge-prompt structure. The dedicated **Scores**
  sub-page (`/docs/evaluation/scores`) is client-rendered and returned only the
  page chrome ("Langfuse"), so no score-creation code is quoted; its data-model
  content is fully covered by the Core Concepts page itself, so coverage is not
  materially reduced.
- Three pages were read end-to-end (Core Concepts, Experiments/Datasets,
  LLM-as-a-Judge). The sidebar also lists "Experiments in CI/CD" and
  "Annotation Queues" sub-pages not separately fetched; their substance is
  summarized by the Core Concepts taxonomy and the SDK examples already
  extracted.
- Quotes were copied from the stripped page text (character-for-character from
  the rendered source). Multi-token spacing artifacts from HTML tokenization
  were normalized to the displayed form (e.g., "NUMERIC, CATEGORICAL, BOOLEAN,
  or TEXT"). The Assayer should spot-check key quotes against the live URLs.
- The reconstruction of the Evaluation Loop as ASCII is derived from the page's
  labeled Deploy/Online/Offline flow, not invented content; it is explicitly
  marked as a reconstruction.
- Source is vendor documentation: claims describe intended product usage, not
  independently benchmarked outcomes. Convergence with PagerDuty's independent
  practitioner account (Claim 10 there) raises overall confidence from "vendor
  claim" to "emerging," which is why `confidence_overall` is set to emerging.
- No part of the source was paywalled; all pages are publicly accessible.
