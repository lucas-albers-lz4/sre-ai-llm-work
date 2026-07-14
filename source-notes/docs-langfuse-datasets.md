---
source_url: https://langfuse.com/docs/evaluation/features/datasets
source_type: docs
title: "Datasets — Langfuse"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: "unknown (Langfuse vendor docs; page footer © 2022–2026)"
date_extracted: 2026-07-14
last_checked: 2026-07-14
status: current
confidence_overall: settled
issue: "#196"
---

# Datasets — Langfuse

> Concrete tool implementation of the abstract "golden-dataset-driven evaluation"
> pattern: Langfuse Datasets are versioned, trace-linked collections of
> (input, expected_output) pairs that back reproducible, deploy-gating experiments.

## Source Context

- **Type**: docs (vendor product documentation)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor; the page documents its own shipped feature set, so claims about the
  tool's behavior are authoritative and factual (settled) rather than opinion.
- **Scope**: The Langfuse **Datasets** feature only — dataset creation, item
  management, versioning, folders, JSON-Schema enforcement, multi-modal items,
  sourcing items from production traces/observations, and running SDK/UI
  experiments against (versioned) datasets. It does NOT cover the separate
  Experiments/CI-CD pages, scoring methods, or the eval-judge layer.

## Extracted Claims

### Claim 1: A Langfuse Dataset is a first-class collection of (input, expected_output) pairs used to test your application, consumed by both UI- and SDK-based experiments
- **Evidence**: Page-definition sentence plus the "Why use datasets?" list
  (create test cases from production traces, collaborate, single source of truth).
- **Confidence**: settled
- **Quote**: "A dataset is a collection of inputs and expected outputs and is used to test your application. Both UI-based and SDK-based experiments support Langfuse Datasets."
- **Our assessment**: This is the core pattern our corpus already advocates in the
  abstract (golden datasets). Langfuse makes it a concrete, named, queryable
  object — the same role PagerDuty's "golden test questions" (Claim 10) and
  Google SRE 01-05's "golden dataset" (Claim 11) play, but as a managed artifact.

### Claim 2: Dataset items can be sourced from real production traces, with each item linked back to its source trace and observation via source_trace_id / source_observation_id
- **Evidence**: "Why use datasets?" lists "Create test cases for your application
  with real production traces." SDK `create_dataset_item` accepts
  `source_trace_id` and `source_observation_id`; UI exposes "+ Add to dataset" on
  any observation of a production trace.
- **Confidence**: settled
- **Quote**: "Create test cases for your application with real production traces"
- **Our assessment**: This is the trace→dataset pipeline the Prospector flagged.
  It is the provenance half of the eval-loop: Honeycomb's Claim 11 attaches eval
  *results* to spans; Langfuse attaches eval *fixtures* to the originating trace,
  closing the loop the other way. High value for Ch02 observability framing.

### Claim 3: Production observations can be batch-added to a dataset directly from the Observations table, with JSON-path field mapping and partial-success handling
- **Evidence**: Dedicated "Batch add observations to datasets" section describing
  filters → checkbox select → Actions → Add to dataset, with field mapping via
  "JSON path expressions" and "support for partial success" (valid items added,
  schema-invalid items logged).
- **Confidence**: settled
- **Quote**: "You can batch add multiple observations to a dataset directly from the observations table. This is useful for quickly building test datasets from production data."
- **Our assessment**: A concrete scaling mechanism for the "build golden datasets
  from production failures" workflow. The partial-success + background-batch
  behavior is an operational detail not present in other notes and worth citing
  when the guide discusses dataset curation at scale.

### Claim 4: Dataset versioning is timestamp-based and append-on-write — every add/update/delete/archive of an item mints a new version; GET APIs return latest by default but accept a `version` timestamp to pin a historical state
- **Evidence**: "Versioning" section: "Every add, update, delete, or archive of
  dataset items produces a new dataset version. Versions track changes over time
  using timestamps." Plus: "GET APIs return the latest version at query time by
  default. You can fetch datasets at specific version timestamps using the version
  parameter." Versioning applies to items only, not schema.
- **Confidence**: settled
- **Quote**: "Every add, update, delete, or archive of dataset items produces a new dataset version. Versions track changes over time using timestamps."
- **Our assessment**: This is the novel, load-bearing reproducibility primitive.
  Unlike semantic versioning, it is an immutable, time-indexed snapshot log. This
  is exactly what makes "reproduce an experiment against the exact dataset state
  from a specific point in time" possible — the prerequisite for gating deploys
  on eval results (Ch05). No existing note specifies a versioning mechanism.

### Claim 5: Experiments can be run against a pinned dataset `version`, enabling reproducible re-runs and before/after dataset comparisons
- **Evidence**: "Run experiments on versioned datasets" section with
  `get_dataset(name, version=...)` then `dataset.run_experiment(...)`. Stated
  benefits: re-run on historical versions after edits/deletes, compare model
  performance before/after dataset changes, reproduce exact prior-run results,
  test improvements against a fixed baseline.
- **Confidence**: settled
- **Quote**: "This approach ensures reproducibility by allowing you to: Re-run experiments on historical dataset versions even after items are updated or deleted"
- **Our assessment**: Directly operationalizes PagerDuty Claim 10's
  "CI-gated re-evaluation" against a *fixed* golden set. The `version` pin is what
  lets a CI gate mean "same dataset the last good run used." Strong Ch05 evidence.

### Claim 6: Datasets are organized into virtual folders by embedding slashes in the dataset name (e.g. "evaluation/qa-dataset")
- **Evidence**: "Dataset Folders" section: "To create a folder, add slashes (/) to
  a dataset name. The UI shows every segment ending with a / as a folder
  automatically." JS/TS must URL-encode the name (`encodeURIComponent`).
- **Confidence**: settled
- **Quote**: "Datasets can be organized into virtual folders to group datasets serving similar use cases."
- **Our assessment**: A small but concrete management pattern for dataset
  sprawl at scale (relevant given Claim 3's batch-build workflow). Low novelty but
  genuinely absent from other notes.

### Claim 7: Datasets optionally enforce JSON Schema on input and/or expected_output; invalid items are rejected with detailed errors, valid items still accepted
- **Evidence**: "Schema Enforcement" section with `input_schema` /
  `expected_output_schema` (Python) and `inputSchema` / `expectedOutputSchema`
  (JS/TS). "Once set, all dataset items are automatically validated against these
  schemas. Valid items are accepted, invalid items are rejected with detailed
  error messages."
- **Confidence**: settled
- **Quote**: "Optionally add JSON Schema validation to your datasets to ensure all dataset items conform to a defined structure."
- **Our assessment**: Data-quality gate at the *fixture* level — complements the
  eval (output) quality gate. Useful reference when the guide covers dataset
  hygiene; no other note describes schema-enforced datasets.

### Claim 8: Dataset items are multi-modal — images/audio/video/documents via LangfuseMedia — but SDK-based experiments only, gated to Python SDK >= 4.10.0 and JS/TS @langfuse/client >= 5.6.0; UI experiments do not yet support media items
- **Evidence**: "Multi-modal dataset items" section; version-gated support
  statement; UI attach via button/drag-drop/paste; SDK wraps media in
  `LangfuseMedia`. "CSV imports are intended for text and structured JSON dataset
  items. Use the UI item editor or SDKs for multi-modal dataset items."
- **Confidence**: settled
- **Quote**: "Dataset item input, expectedOutput, and metadata fields can include media attachments such as images, audio, video, documents, and other files."
- **Our assessment**: Relevant for multimodal-agent eval patterns. The version
  gate + UI-experiment limitation are precise constraints worth recording so the
  guide doesn't over-claim multimodal eval support.

### Claim 9: Synthetic dataset items can bootstrap a dataset by prompting an LLM to generate common questions/tasks
- **Evidence**: "Create synthetic datasets" section: "Frequently, you want to
  create synthetic examples to test your application to bootstrap your dataset.
  LLMs are great at generating these by prompting for common questions/tasks."
  (Links to a "Synthetic Datasets" cookbook notebook.)
- **Confidence**: settled
- **Quote**: "Frequently, you want to create synthetic examples to test your application to bootstrap your dataset. LLMs are great at generating these by prompting for common questions/tasks."
- **Our assessment**: Documents the synthetic-data bootstrapping pattern. Lower
  priority than the production-trace path (Claim 2), but a legitimate, commonly
  used curation strategy.

### Claim 10: Archiving (not deleting) a dataset item removes it from future experiment runs — a soft-delete retention semantics
- **Evidence**: "Edit/archive dataset items" section: "Archiving items will remove
  them from future experiment runs." SDK upserts item with `status="ARCHIVED"`.
- **Confidence**: settled
- **Quote**: "Archiving items will remove them from future experiment runs."
- **Our assessment**: The soft-delete semantics matter for versioning integrity —
  archived items disappear from the *latest* view but remain reachable via a
  historical `version` timestamp (Claim 4/5). A precise operational detail.

### Claim 11: CSV import is restricted to text/structured-JSON items; multi-modal items must use the UI editor or SDKs
- **Evidence**: "CSV imports are intended for text and structured JSON dataset
  items. Use the UI item editor or SDKs for multi-modal dataset items."
- **Confidence**: settled
- **Quote**: "CSV imports are intended for text and structured JSON dataset items. Use the UI item editor or SDKs for multi-modal dataset items."
- **Our assessment**: A concrete workflow constraint bounding Claim 8. Minor but
  prevents over-generalizing "import your eval set from CSV" to multimodal data.

## Concrete Artifacts

### Creating a dataset (Python SDK) — name unique per project; optional metadata
```python
langfuse.create_dataset(
    name="<dataset_name>",
    # optional description
    description="My first dataset",
    # optional metadata
    metadata={
        "author": "Alice",
        "date": "2022-01-01",
        "type": "benchmark",
    },
)
```

### Adding an item sourced from a production trace (Python SDK) — source_trace_id / source_observation_id link the fixture to its origin
```python
langfuse.create_dataset_item(
    dataset_name="<dataset_name>",
    input={"text": "hello world"},
    expected_output={"text": "hello world"},
    # link to a trace
    source_trace_id="<trace_id>",
    # optional: link to a specific span, event, or generation
    source_observation_id="<observation_id>",
)
```

### Multi-modal item via LangfuseMedia (Python SDK)
```python
from langfuse.media import LangfuseMedia

langfuse.create_dataset_item(
    dataset_name="visual-qa",
    input={
        "question": "What is shown in this image?",
        "image": LangfuseMedia(
            file_path="./example.jpg",
            content_type="image/jpeg",
        ),
    },
    expected_output={"label": "invoice"},
)
```

### Timestamp-based versioning + running an experiment against a pinned version (Python SDK) — the reproducibility primitive
```python
from datetime import datetime, timezone
from langfuse import Langfuse

langfuse = Langfuse()

version_timestamp = datetime(2025, 12, 15, 6, 30, 0, tzinfo=timezone.utc)

# Fetch versioned dataset as of a point in time
versioned_dataset = langfuse.get_dataset("qa-dataset", version=version_timestamp)

# Run experiment against that exact dataset state
def my_llm_application(*, item, **kwargs):
    return item.expected_output

result = versioned_dataset.run_experiment(
    name="Baseline Experiment v1",
    description="Running on dataset v1",
    task=my_llm_application,
)
```
Note (from source): "GET APIs return the latest version at query time by default.
You can fetch datasets at specific version timestamps using the version
parameter." Versioning applies to dataset *items* only, not dataset *schema*.

### JSON Schema enforcement at dataset creation (Python SDK)
```python
langfuse.create_dataset(
    name="qa-conversations",
    input_schema={
        "type": "object",
        "properties": {
            "messages": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "role": {"type": "string", "enum": ["user", "assistant", "system"]},
                        "content": {"type": "string"},
                    },
                    "required": ["role", "content"],
                },
            }
        },
        "required": ["messages"],
    },
    expected_output_schema={
        "type": "object",
        "properties": {"response": {"type": "string"}},
        "required": ["response"],
    },
)
```

### JS/TS SDK equivalents (abridged)
```javascript
import { LangfuseClient } from "@langfuse/client";
const langfuse = new LangfuseClient();

// create dataset
await langfuse.api.datasets.create({
  name: "<dataset_name>",
  description: "My first dataset",
  metadata: { author: "Alice", date: "2022-01-01", type: "benchmark" },
});

// add item (incl. media)
await langfuse.dataset.createItem({
  datasetName: "<dataset_name>",
  input: { text: "hello world" },
  expectedOutput: { text: "hello world" },
  sourceTraceId: "<trace_id>",          // link to production trace
  sourceObservationId: "<observation_id>",
});

// fetch versioned dataset (name must be URL-encoded when it contains "/")
const encodedName = encodeURIComponent("evaluation/qa-dataset");
const versionedDataset = await langfuse.dataset.get("my-dataset", {
  version: new Date("2025-12-15T06:30:00").toISOString(),
});
const result = await versionedDataset.runExperiment({
  name: "Baseline Experiment v1",
  description: "Running on dataset v1",
  task: async (item) => item.expectedOutput,
});
```

## Cross-References

- **Corroborates**:
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 10** — golden datasets +
    LLM-as-a-judge + CI gates. Langfuse Datasets are the concrete managed
    artifact for PagerDuty's "golden test questions"; Claim 5's versioned
    `run_experiment` is the deploy-gate-friendly realization of PagerDuty's
    "CI-gated re-evaluation on any model/prompt/tool change."
  - `blog-pagerduty-production-ai-agent-gaps.md` **Claim 15** — "deterministic
    software tests do not work well with natural language systems, where there is
    no single correct output." Langfuse's (input, expected_output) dataset +
    experiment model is the tooling answer to that gap (eval against expected
    outputs rather than exact-match asserts).
  - `docs-google-sre-prodcast-01-05-client-transparent-migrations.md` **Claim 11**
    — production-traffic replay / dark launch, which the note itself calls "the
    SRE ancestor of evaluating an AI agent against a golden dataset before
    promotion." Langfuse's versioned, trace-linked datasets are the AI-native
    form of that replay fixture. Also **Claim 12/13** (replay "do no harm" / never
    mutate state) — a useful constraint when the guide discusses replaying
    captured fixtures.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 11** —
    eval results attached as span events (`gen_ai.evaluation.result`) to GenAI
    operation spans. Langfuse's `source_trace_id` is the *provenance* mirror: the
    eval fixture is linked back to the originating production trace, closing the
    cost/latency/quality loop from the input side.
- **Extends**: Implements the abstract golden-dataset pattern that PagerDuty
  Claim 10 and Google SRE 01-05 Claim 11 describe, down to SDK calls, versioning
  semantics, and schema enforcement. It is the "how" for their "what."
- **Novel** (not covered by existing notes):
  - Timestamp-indexed, immutable-on-write dataset versioning via a `version`
    parameter that pins a historical snapshot (Claim 4/5).
  - Folder organization through slashes in dataset names (Claim 6).
  - JSON-Schema enforcement at the dataset level (`input_schema` /
    `expected_output_schema`) (Claim 7).
  - Multi-modal dataset items via `LangfuseMedia`, with explicit SDK-version
    gates and a UI-experiment limitation (Claim 8/11).
  - Batch observations→dataset with JSON-path field mapping and partial-success
    handling (Claim 3).
  - `source_trace_id` / `source_observation_id` linking of dataset items to
    production traces (Claim 2).
- **Contradicts**: None found. The page is consistent with the corpus's
  golden-dataset/eval discipline; it adds tool-specific mechanism, not
  opposing advice. No contradiction issue filed.

## Guide Impact

- **Chapter 02 (Observability)**: Add a provenance note — evaluation fixtures
  should be trace-linked (`source_trace_id`) so an eval failure can be traced
  back to the real production input that produced it. This complements Honeycomb
  Claim 11 (eval results on spans) and makes the eval loop bidirectional.
  Evidence: Claim 2.
- **Chapter 05 (LLM Ops Reliability — eval harnesses that gate deploys)**: This
  is the highest-value target. Recommend adding the "versioned dataset as the
  deploy-gate fixture" pattern: pin a dataset `version` timestamp in CI so the
  eval gate runs against the *exact* golden set the last good deploy used
  (reproducibility + before/after comparison), directly implementing PagerDuty
  Claim 10's CI-gated re-evaluation with a concrete, vendor-documented mechanism.
  Evidence: Claim 4, Claim 5, plus Concrete Artifacts (versioned
  `get_dataset` + `run_experiment`). Also worth a one-line pointer to dataset
  folders (Claim 6) and JSON-Schema enforcement (Claim 7) as dataset-hygiene
  practices at scale.
- **Not recommended**: Do not present Langfuse as the only way to do
  golden-dataset eval (it's one tool); keep the PagerDuty/Google SRE patterns as
  the tool-agnostic spine and cite this note as a worked example.

## Extraction Notes

- Source fetched 2026-07-14. WebFetch returned empty for this page (JS-heavy
  Next.js render), so the page was retrieved with `curl` and the readable text
  extracted from the HTML (`<script>`/`<style>` stripped, entities decoded).
  Code blocks were re-formatted from the extracted tokens into valid Langfuse SDK
  syntax (the HTML extraction had injected spaces around punctuation inside code
  spans); the reformatting matches the documented API surface and is faithful to
  the rendered page.
- Quotes are taken from the rendered-page text (no extraction artifacts). The
  page footer reads "© 2022–2026 Langfuse GmbH / Finto Technologies Inc."; no
  explicit single publish date is exposed, so `date_published` is left as
  "unknown" with the footer range noted.
- Second Prospector triage assessed novelty as **low** (incremental tool-specific
  detail over PagerDuty/Google SRE). That assessment is respected here: the note
  foregrounds the genuinely novel mechanism (timestamp versioning, schema
  enforcement, trace-linking, multimodal gating) and frames the rest as a
  corroborating worked example rather than new doctrine. `confidence_overall` is
  **settled** because vendor docs of a shipped feature are factual, but the
  surrounding *pattern* remains "emerging" in the corpus (PagerDuty Claim 10).
