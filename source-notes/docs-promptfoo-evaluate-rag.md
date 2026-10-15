---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-rag
source_type: docs
title: "Evaluating RAG pipelines"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-15
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: emerging
issue: "#1725"
---

# Evaluating RAG pipelines

> The vendor's composition-level RAG eval tutorial: split retrieval and
> generation into separately measured stages, wire a custom retrieval script
> into the same eval matrix as generation via the `file://` Python provider
> contract, compare vector databases by listing one retrieval script per store
> as providers — and, the genuinely new claim, a cross-lingual
> metric-selection matrix that says text-matching retrieval metrics
> (notably `context-recall`) collapse when query and context languages
> differ, with vendor-asserted accuracy figures that carry no methodology.

## Source Context

- **Type**: docs (vendor tutorial — promptfoo `guides/evaluate-rag`, under
  Evals → Guides → Evaluation Techniques; auto-discovered from the registered
  `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party tutorial assembling
  the vendor's own assertion types into a staged RAG eval — the config
  shapes and provider mechanics are authoritative and directly checkable
  against an installed CLI, but vendor-positioned: the page carries no
  benchmark, dataset, language pair, sample size, or methodology behind its
  cross-lingual accuracy figures, and no measured run of the worked examples.
- **Scope**: Stage-split RAG eval design (retrieval-only, generation-only,
  end-to-end); the `file://retrieve.py` Python provider mechanics
  (`call_api`, `pythonExecutable`, `PROMPTFOO_PYTHON`); retrieval assertions
  (`contains-all` over document names); multi-vector-DB comparison harness;
  output-based vs context-based metric taxonomy; dynamic context via scripted
  `get_var`; context-vars vs `contextTransform` extraction (with multi-language
  JS extraction examples); prompt/model comparison; and the Multi-lingual RAG
  Evaluation section. Does NOT cover: latency, throughput, caching, timeouts,
  CI exit-code gating, cost figures, red-teaming, or the per-type semantics of
  any assertion (those live on the per-type reference pages, already mined).
- **Last updated**: the page footer reads "Last updated on **Oct 15, 2026** by
  **renovate\[bot\]**" — same day as extraction. No canonical first-published
  date, so `date_published` carries the last-updated date (same convention as
  the sibling `docs-promptfoo-*` notes).

## Extracted Claims

### Claim 1: A RAG eval should measure document retrieval and LLM generation as *separately gated* stages, because stage separation is what localizes failures
- **Evidence**: The page's opening evaluation-strategy statement, which
  numbers the two steps and gives the rationale in one sentence.
- **Confidence**: settled (documented design guidance; the rationale is
  asserted, not measured, but the decomposition itself is uncontroversial
  and matches the corpus's existing chain-testing material)
- **Quote**: "When designing an evaluation strategy for RAG applications, you should evaluate both steps:

  1.  Document retrieval from the vector store
  2.  LLM output generation

  It's important to evaluate these steps separately, because breaking your RAG into multiple steps makes it easier to pinpoint issues."
- **Our assessment**: The RAG-specific instance of the unit-vs-end-to-end
  split `docs-promptfoo-testing-llm-chains.md` (#1575) Claim 1 already
  documents for LLM chains generally — that note frames the choice as "unit
  tests per step" vs "end to end"; this page *prescribes* the split for RAG
  and then builds the whole tutorial on it. The failure-localization
  argument is the same one SREs make for stage-level SLIs: a green
  end-to-end eval over a broken retriever (the model answers faithfully
  from wrong documents) is indistinguishable from a model regression unless
  the retrieval stage has its own gate. We buy the guidance; the page itself
  does not demonstrate the localization with a worked failure, so it stays
  design advice rather than evidence.

### Claim 2: The retrieval step is evaluated in isolation by wrapping it as a `file://` Python *provider* — a `retrieve.py` exposing `call_api(query, options, context)` — which the Node CLI satisfies by starting a Python worker per call, with no separate Python package or server
- **Evidence**: The "How Promptfoo runs Python retrieval scripts" section:
  the worker-invocation mechanism, the first-argument rendering note, and
  the explicit "no package or server" boundary.
- **Confidence**: settled (documented product behavior; checkable against
  an installed CLI)
- **Quote**: "The `file://retrieve.py` provider is still run from the normal Node-based Promptfoo CLI. When `promptfoo eval` reaches that provider, it starts a Python worker, imports `retrieve.py`, and calls `call_api(prompt, options, context)` for each test case. The first argument is the rendered prompt, which is the `{{ query }}` value in this example. You do not need a separate Promptfoo Python package or server."
- **Our assessment**: The load-bearing mechanics that make the stage-split
  pattern adoptable: retrieval lives in the same eval matrix as generation
  because the provider contract (`call_api(prompt, options, context)` →
  `{output}`) is language-agnostic at the boundary. This is the same
  module-level `call_api` contract `docs-promptfoo-evaluate-crewai.md`
  Claim 2 documents for a CrewAI agent wrapper — corroborating that the
  Python provider entrypoint is a framework-level contract, not a
  RAG-specific one. Note the parameter-name slide the page itself performs:
  the signature is `call_api(query, options, context)` in the script, but
  the harness passes the *rendered prompt* as the first argument (the
  `{{ query }}` var rendered into the placeholder prompt). The "query" is
  a naming convention of the example, not a special harness channel.

### Claim 3: The Python interpreter for a `file://` provider is pinned two ways — per-provider `pythonExecutable: ./.venv/bin/python` or the global `PROMPTFOO_PYTHON` default — the same knobs the assertions page documents, now on the provider surface
- **Evidence**: The venv installation snippet, the per-provider config
  example, and the env-var sentence in "How Promptfoo runs Python retrieval
  scripts."
- **Confidence**: settled (documented product behavior; the knobs are
  documented on two independent vendor pages)
- **Quote**: "If you do not want to activate the virtual environment before running Promptfoo, point the provider at the environment's Python executable:" and "You can also set `PROMPTFOO_PYTHON=/path/to/python` as a global default when the provider does not specify `pythonExecutable`."
- **Our assessment**: Corroboration, not a novel finding —
  `docs-promptfoo-python-assertions.md` (#1499) Claim 1 already extracted
  both knobs (via its `/docs/integrations/python/` sub-page) as the fix for
  the "slim CI image ships only `python3`" failure. The value here is the
  second independent surface: a *retrieval provider* is the same
  interpreter dependency the assertion path has, so the guide's "pin
  `PROMPTFOO_PYTHON` as part of the gate's definition" rule
  (#1499 Guide Impact) applies to the retrieval stage too — a RAG eval's
  retrieval gate inherits the runner image's Python installation exactly as
  a `type: python` assertion does.

### Claim 4: A custom retrieval provider's result dict may carry `error` and `tokenUsage` (prompt/completion/total), giving the retrieval stage its own failure channel and per-call cost attribution inside the eval report
- **Evidence**: The commented stub inside the page's `retrieve.py` example
  (see Concrete Artifacts) — both fields appear as commented code with
  "Include error handling and token usage reporting as needed."
- **Confidence**: settled that the page documents the surface (the comments
  are the documentation); the aggregation/display behavior of these fields
  in the eval report is not shown on this page
- **Quote**: "# if token_usage_calculated:
    #     result['tokenUsage'] = {"total": token_count, "prompt": prompt_token_count, "completion": completion_token_count}"
- **Our assessment**: The per-request cost-attribution hook the Prospector
  flagged for Ch02: a retrieval provider that reports `tokenUsage` makes
  the retrieval stage's token spend visible per test case, the same
  multi-call footprint preservation
  `docs-promptfoo-evaluate-openai-agents-python.md` (#1707) Claim 7
  documents for the OpenAI-Agents provider (`tokenUsage.numRequests`,
  cached-input tokens). Corroborates that `tokenUsage` on a custom
  provider's return dict is a framework contract, not an SDK-bridge
  quirk. Caveat: this page shows the field in a comment, never a worked
  report view, so "per-call cost attribution appears in the UI" is
  *not* established — only the return-channel shape is.

### Claim 5: The retrieval-only eval uses a placeholder `{{ query }}` prompt and gates on `contains-all` over expected document names/metadata substrings — and the surrounding prose references `context-recall` assertions that do not appear in the worked config
- **Evidence**: The retrieval `promptfooconfig.yaml` (verbatim in Concrete
  Artifacts) whose asserts are exclusively `contains-all`, against the
  Configuration section's sentence about `context-recall` assertions.
- **Confidence**: settled for the config shape; the prose/config mismatch
  is a verified documentation gap on the page
- **Quote**: "In the above example, the `contains-all` assertion ensures that the output from `retrieve.py` contains all the listed substrings. The `context-recall` assertions use an LLM model to ensure that the retrieval performs well."
- **Our assessment**: Two things. First, the retrieval gate's unit is
  *document-name presence* — deliberately weak, deterministic, and cheap:
  it catches "the retriever returned the wrong documents" but not "the
  documents are insufficient for the answer," which is what the
  ground-truth-bound `context-recall` gate exists for
  (`docs-promptfoo-model-graded-context-recall.md` (#1332) Claims 1, 4).
  Second, the page's own example never wires a `context-recall` assert,
  so the prose sentence describes a gate the config does not contain — a
  reader copying the example gets a contains-all-only retrieval gate and
  may believe they have LLM-graded retrieval quality. Record the gap; the
  vendor's RAG-example repo (linked at the page bottom) was not fetched to
  check whether it closes it.

### Claim 6: Vector databases are compared by listing one retrieval script per store in `providers`, producing a side-by-side eval view — and the vendor explicitly disowns the ranking its own example shows
- **Evidence**: The "Comparing vector databases" section: the three-script
  providers list, the comparison-view screenshot reference, and the
  results-vary caveat.
- **Quote**: "In this particular example, the metrics that we set up indicate that PGVector performs the best. But results will vary based on how you tune the database and how you format or transform the query before sending it to the database."
- **Confidence**: settled (documented pattern plus vendor caveat)
- **Our assessment**: The harness shape is the extractable artifact: N
  retrieval implementations behind one provider contract, one eval matrix,
  one comparison view — the same multi-provider diffing surface the prompt
  and model comparison sections use, applied to infrastructure choice.
  The vendor's own honesty caveat is the more important half for the
  guide: a single eval run of three untuned stores is a *smoke test*, not
  a procurement decision, and the page says so. The "PGVector performs
  the best" line must not be laundered into guide advice — it is
  explicitly conditional on tuning and query transformation, and the page
  gives no tuning parameters, store versions, dataset, or metric weights
  behind it. We capture the harness, dismiss the ranking.

### Claim 7: The tutorial's metric taxonomy is stage-keyed — output-based (factuality/correctness, answer-relevance) vs context-based (context-adherence/grounding/faithfulness, context-recall, context-relevance) vs custom metrics — so the assertion catalog is read as "which stage's failure does this gate catch"
- **Evidence**: The intro's three-bullet criteria list with per-metric
  one-line definitions (verbatim in Concrete Artifacts).
- **Confidence**: settled (documented taxonomy; consistent with the
  per-type reference pages' definitions)
- **Quote**: "-   Context-based
    -   **Context recall**: Measures whether the context contains the correct information, compared to a provided ground truth, in order to produce an answer."
- **Our assessment**: The composition story the corpus's per-type notes
  structurally lack: #1332 (recall), #1320 (faithfulness), #1319
  (answer-relevance), and #1348 (factuality) each document one metric's
  contract in isolation; this page is the first mined source that arranges
  them by *failure stage* and tells a team which member answers which
  question. Note the naming looseness — "Context adherence (also called
  Grounding or Faithfulness)" — which conflates the vendor's own
  `context-adherence`/`context-faithfulness` branding in a way the
  per-type pages do not; a reader should trust the per-type pages for
  assert-type names. Also note "Factuality (also called Correctness)".
  The taxonomy itself does not contradict the mirror-direction framing in
  #1332 Claim 4 / #1320 Claim 1 — it is the same partition at tutorial
  altitude.

### Claim 8: Dynamic per-case context is fetched by a scripted test var — `context: file://./load_context.py` with a `get_var(var_name, prompt, other_vars)` entrypoint returning `{output}` — which is the configuration-guide's documented scripted-var API applied to vector-DB retrieval
- **Evidence**: The "Using dynamic context" section: the config snippet
  wiring `file://./load_context.py` as the `context` var, and the
  two-function script (`retrieve_documents` + `get_var`) with the
  special-entrypoint sentence.
- **Quote**: "`get_var(var_name, prompt, other_vars)`: This is a special function that promptfoo looks for when loading dynamic variables."
- **Confidence**: settled (documented product behavior; identical signature
  to the configuration-guide page)
- **Our assessment**: Direct corroboration of
  `docs-promptfoo-configuration-guide.md` (#1513) Claim 10 — that note
  already documents the Python scripted-var signature
  `get_var(var_name, prompt, other_vars)` returning `{output}` or
  `{error}` **and names vector databases as the use case** ("Scripted vars
  are useful when testing vector databases like Pinecone, Chroma, Milvus,
  etc."). This page adds the RAG-worked form of exactly that pattern. The
  reproducibility caution from #1513's Claim 10 assessment transfers
  unchanged: a suite whose `context` var hits a live vector store at eval
  time grades inputs that cannot be reconstructed from the config — the
  evidence-integrity problem from the input side. Prefer fixture contexts
  (`context: file://docs/reimbursement.md`, as the page's static sections
  do) for gates; reserve scripted retrieval vars for retrieval *development*.

### Claim 9: Context for context-based asserts can be supplied as a test var or extracted from the provider's response via `contextTransform`, and both `contextTransform` and `options.transform` receive the provider's raw output — so answer and documents can be extracted independently; the page adds multi-language JS extraction examples on top of that settled pipeline position
- **Evidence**: The "Context evaluation approaches" section: the two
  approaches' configs, the "Important for RAG evaluations" callout, and
  the three "Common patterns" JS expressions (including the AWS Bedrock
  Knowledge Base citation extraction).
- **Quote**: "The `contextTransform` and `options.transform` both receive the provider's output directly. This ensures that context extraction works reliably even when the main output is transformed for other assertions."
- **Confidence**: settled for the pipeline position (documented product
  behavior, independently extracted); the JS expressions are documented
  but unexecuted examples
- **Our assessment**: The transform-stage contract is **already settled**
  in `docs-promptfoo-configuration-guide.md` (#1513) Claim 1 — that note
  extracted the three-stage order (provider `transformResponse` first,
  then `options.transform`/`contextTransform` both from that output, then
  assertion-level `transform`) — so per the Prospector's instruction this
  note does **not** re-mine it; this page's callout is a corroborating
  restatement, cited, not re-claimed. What is genuinely additive here is
  the extraction recipes: array-of-objects joins
  (`output.documents.map(d => d.content).join("\n")`), the null-fallback
  idiom (`output.context || output.retrieved_content || "No context"`),
  and the nested-metadata Bedrock case
  (`output.citations?.[0]?.content?.text || ""`) — multi-language
  instances of #1305 Claim 13's non-empty-string mandate. Caution
  inherited from #1305: the fallback idiom *itself* is the auditable
  condition — a transform that silently degrades to `"No context"` becomes
  the string the judge grades against, invisible in the pass/fail report.

### Claim 10: Cross-lingually (query and context in different languages), text-matching metrics collapse while concept-based metrics survive — the page's matrix recommends `context-relevance` (85–95% accuracy), `context-faithfulness` (70–80%), `answer-relevance` (65–75%), prescribes `llm-rubric` in place of `context-recall` ("Drops from 80% to 10-30% accuracy") and all string metrics, and attributes the collapse to textual matching vs conceptual relationships — but the figures carry no benchmark, language pair, dataset, sample size, or methodology
- **Evidence**: The entire "Multi-lingual RAG Evaluation" section: the
  mechanism framing, the per-metric accuracy headings, the
  context-recall-avoidance rationale with the Paris/París example, the
  string-metrics dismissal, and the worked cross-lingual config with
  lowered thresholds (0.85 / 0.70 / 0.65) and a concept-coverage
  `llm-rubric`.
- **Confidence**: emerging for the *direction* (text-match fails
  cross-lingually, concept-match survives — plausible, consistent with
  the measurement-portability literature, and the mechanism story is
  coherent); **anecdotal/unquantified for the numbers** — they are bare
  vendor assertions with zero provenance, so they are recorded here with
  their provenance status and must not enter the guide as measured facts
- **Quote**: "When documents and queries are in different languages, traditional evaluation metrics can fail dramatically. The key distinction is between metrics that evaluate **conceptual relationships** versus those that rely on **textual matching**." and "This metric attempts to verify that the context contains specific expected information by matching text. When your expected answer is "The capital is Paris" but your context says "La capital es París," the metric fails to recognize the match. **Use `llm-rubric` instead** to check for concept coverage." and "These traditional NLP metrics measure surface-level text similarity - comparing characters, words, or n-grams. They have no understanding that "dog" and "perro" mean the same thing. They'll report near-zero similarity for semantically identical content in different languages."
- **Our assessment**: The genuinely new claim of this page, and the one the
  Assayer should scrutinize hardest. What we buy: (a) the *direction* — a
  surface-text metric scores "Paris" vs "París" as a miss and an LLM-judge
  concept metric does not, which is uncontroversial; (b) the operational
  recipe — pin the answer language in the prompt (the page warns "When
  context and query are in different languages, LLMs may respond in
  either language"), lower thresholds, swap `context-recall` for an
  `llm-rubric` concept-coverage rubric. What we do **not** buy as
  evidence: every percentage. Per Ch05's "Metrics without a unit are
  noise," these figures have no unit — no dataset, language pair, judge
  model, sample size, or measurement procedure is stated anywhere on the
  page, and the same vendor's per-type reference pages carry no
  calibration data that would corroborate them. Record the numbers as
  vendor-asserted and unquantified; the extractable claim is the ranking
  direction (concept-based > text-matching cross-lingually) and the
  recipe, not the values. The page is also the eval-side instance of the
  metric-portability theme `blog-promptfoo-asr-not-portable-metric.md`
  (#261) Claim 1 establishes for red-team metrics: a score is a property
  of the metric *and* the input distribution (here: the language-pair
  distribution), not of the system alone. One internal tension to record:
  this page characterizes `context-recall` as "matching text," while
  #1332 Claim 1 documents the same metric as LLM statement-attribution
  ("Breaks the expected answer into statements and checks if each can be
  attributed to the context"). The mechanism stories differ; both vendor
  pages agree on the practical cross-lingual conclusion (don't rely on it
  cross-lingually; use `llm-rubric`), so no forking guide advice results
  and no contradiction issue is filed (see Cross-References).

### Claim 11: End-to-end RAG eval is the same script-provider composition with combined `retrieve_and_generate_v*.py` providers — the stage-split harness composed, not a separate mode
- **Evidence**: The "Evaluating end-to-end performance" section's config
  listing two combined scripts as providers, plus the pointer to the
  full example repo.
- **Quote**: "The way to do this is similar to the "Evaluating document retrieval" step above. You'll have to create a script that performs document retrieval and calls the LLM, then set up a config like this"
- **Confidence**: settled (documented pattern)
- **Our assessment**: Small but structurally important claim: the tutorial
  closes the loop by showing that "separately measured stages" and "one
  end-to-end gate" are not two tools but two provider listings over the
  same code — the retrieval-only script and the combined script share the
  `call_api` contract, so a team can promote a stage gate to an e2e gate
  by composition. This is the RAG-shaped completion of #1575 Claim 1's
  unit-vs-e2e choice; the guide can state it as "write the retrieval
  script and the combined script, gate on both."

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/guides/evaluate-rag (sections as noted).
Code blocks re-flowed only at the newline level to restore line breaks
lost in HTML extraction, consistent with the sibling promptfoo notes.

### `retrieve.py` retrieval provider (verbatim from "Evaluating document retrieval")

```python
import vectorstore

def call_api(query, options, context):
    # Fetch relevant documents and join them into a string result.
    documents = vectorstore.query(query)
    output = "\n".join(f'{doc.name}: {doc.content}' for doc in documents)
    result = {
        "output": output,
    }
    # Include error handling and token usage reporting as needed
    # if some_error_condition:
    #     result['error'] = "An error occurred during processing"
    #
    # if token_usage_calculated:
    #     result['tokenUsage'] = {"total": token_count, "prompt": prompt_token_count, "completion": completion_token_count}
    return result
```

### Python provider interpreter pinning (verbatim from "How Promptfoo runs Python retrieval scripts")

```yaml
providers:
  - id: file://retrieve.py
    config:
      pythonExecutable: ./.venv/bin/python
```

### Retrieval-only eval config (verbatim from "Configuration")

```yaml
prompts:
  - '{{ query }}'
providers:
  - file://retrieve.py
tests:
  - vars:
      query: What is our reimbursement policy?
    assert:
      - type: contains-all
        value:
          - 'reimbursement.md'
          - 'hr-policies.html'
          - 'Employee Reimbursement Policy'
  - vars:
      query: How many weeks is maternity leave?
    assert:
      - type: contains-all
        value:
          - 'parental-leave.md'
          - 'hr-policies.html'
          - 'Maternity Leave'
```

### Multi-vector-DB comparison providers list (verbatim from "Comparing vector databases")

```yaml
providers:
  - file://retrieve_pinecone.py
  - file://retrieve_milvus.py
  - file://retrieve_pgvector.py
```

### Metric taxonomy (verbatim from the page intro)

```
-   Output-based
    -   **Factuality** (also called Correctness): Measures whether the LLM outputs are based on the provided ground truth. See the [`factuality`](/docs/configuration/expected-outputs/model-graded/) metric.
    -   **Answer relevance**: Measures how directly the answer addresses the question. See [`answer-relevance`](/docs/configuration/expected-outputs/model-graded/) or [`similar`](/docs/configuration/expected-outputs/similar/) metric.
-   Context-based
    -   **Context adherence** (also called Grounding or Faithfulness): Measures whether LLM outputs are based on the provided context. See [`context-adherence`](/docs/configuration/expected-outputs/model-graded/) metric.
    -   **Context recall**: Measures whether the context contains the correct information, compared to a provided ground truth, in order to produce an answer. See [`context-recall`](/docs/configuration/expected-outputs/model-graded/) metric.
    -   **Context relevance**: Measures how much of the context is necessary to answer a given query. See [`context-relevance`](/docs/configuration/expected-outputs/model-graded/) metric.
-   **Custom metrics**: You know your application better than anyone else. Create test cases that focus on things that matter to you (examples include: whether a certain document is cited, whether the response is too long, etc.)
```

### Dynamic context script (verbatim from "Using dynamic context")

```python
def retrieve_documents(question: str) -> str:
    # Calculate embeddings, search vector db...
    return f'<Documents similar to {question}>'

def get_var(var_name, prompt, other_vars):
    question = other_vars['question']
    context = retrieve_documents(question)
    return {
        'output': context
    }
    # In case of error:
    # return {
    #     'error': 'Error message'
    # }
```

### Independent answer/context extraction (verbatim from "Context evaluation approaches" → "Important for RAG evaluations")

```yaml
options:
  transform: 'output.answer' # Extract just the answer for assertions
assert:
  - type: context-faithfulness
    contextTransform: 'output.documents' # Still has access to documents
```

### Multi-language contextTransform patterns (verbatim from "Common patterns")

```
# Extract from array of objects
contextTransform: 'output.documents.map(d => d.content).join("\n")'
# Handle missing data with fallback
contextTransform: 'output.context || output.retrieved_content || "No context"'
# Extract from nested metadata (e.g., AWS Bedrock Knowledge Base)
contextTransform: 'output.citations?.[0]?.content?.text || ""'
```

### Cross-lingual accuracy matrix — headings as printed on the page (vendor-asserted, uncited)

```
context-relevance      (Best performer: 85-95% accuracy)
context-faithfulness   (70-80% accuracy)
answer-relevance       (65-75% accuracy)
llm-rubric             (Highly flexible)
context-recall         (Drops from 80% to 10-30% accuracy)  — avoid
String-based metrics (Levenshtein, ROUGE, BLEU)             — avoid
```

No benchmark, language pair, dataset, sample size, judge model, or
methodology is stated anywhere on the page for any figure above.

### Cross-lingual eval config with lowered thresholds and rubric swap (verbatim from "Practical Configuration")

```yaml
# Cross-lingual evaluation (e.g., English queries, Spanish documents)
tests:
  - vars:
      query: 'What are the benefits of solar energy?'
      # Context is in Spanish while query is in English
      context: |
        La energía solar ofrece numerosos beneficios.
        Produce energía limpia sin emisiones.
        Los costos operativos son muy bajos.
        Proporciona independencia energética.
    assert:
      # These metrics work well cross-lingually
      - type: context-relevance
        threshold: 0.85 # Stays high because it evaluates concepts, not text
      - type: context-faithfulness
        threshold: 0.70 # Reduced from 0.90 baseline due to cross-lingual processing
      - type: answer-relevance
        threshold: 0.65 # Lower threshold when answer language may differ from query
      # DON'T use context-recall for cross-lingual
      # Instead, use llm-rubric to check for specific concepts
      - type: llm-rubric
        value: |
          Check if the answer correctly uses information about:
          1. Clean energy without emissions
          2. Low operational costs
          3. Energy independence
          Score based on coverage of these points.
        threshold: 0.75
```

### Length-penalty defaultTest heuristic (verbatim from "Comparing models")

```yaml
defaultTest:
  assert:
    - type: python
      value: max(0, min(1, 1 - (len(output) - 100) / 900))
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 1** (the
    three-stage transform pipeline: `contextTransform` and `options.transform`
    "both receive the output from the provider transform") — this page's
    "Important for RAG evaluations" callout (Claim 9 here) is an independent
    vendor restatement of the same pipeline position in a RAG worked example.
    Cited, not re-mined, per the Prospector's instruction. (Verified: #1513
    Claim 1.)
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 10** (Python
    scripted vars: `get_var(var_name, prompt, other_vars)` returning
    `{output}`/`{error}`, with vector databases named as the use case) —
    this page's `load_context.py` dynamic-context pattern (Claim 8) is that
    exact API applied to RAG retrieval. (Verified: #1513 Claim 10.)
  - `source-notes/docs-promptfoo-python-assertions.md` **Claim 1**
    (`PROMPTFOO_PYTHON` and per-provider `pythonExecutable` as the
    interpreter-pinning knobs) — this page's provider-side pinning (Claim 3)
    is the same knobs on the provider surface, so the interpreter is a gate
    input for the retrieval stage exactly as for assertions. (Verified:
    #1499 Claim 1.)
  - `source-notes/docs-promptfoo-evaluate-crewai.md` **Claim 2** (module-level
    `call_api(prompt, options, context)` Python provider contract) — this
    page's `retrieve.py` entrypoint (Claim 2) is the retrieval-stage instance
    of the same contract. (Verified: that note's Claim 2.)
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` **Claim 7**
    (`tokenUsage` fields returned from a custom Python provider preserving the
    multi-call footprint) — this page's `tokenUsage` stub in `retrieve.py`
    (Claim 4) corroborates that `tokenUsage` on a custom provider's return
    dict is a framework-level surface. (Verified: #1707 Claim 7.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 8** (the
    multilingual `rubricPrompt` override works uniformly only for
    `llm-rubric`/`g-eval`/`model-graded-closedqa`; `factuality` and
    `context-recall` need assertion-specific prompts) — this page's
    cross-lingual recipe (Claim 10) is consistent: it prescribes `llm-rubric`
    (the family whose rubric swap *is* uniform) as the concept-coverage
    replacement and tells readers to avoid `context-recall` rather than try
    to re-skin it. The two sources constrain the same family boundary from
    different directions. (Verified: #1305 Claim 8.)
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` **Claim 4**
    (recall and faithfulness catch disjoint failure classes — retrieval
    completeness vs output fidelity) — this page's stage-split taxonomy
    (Claim 7) is the tutorial-altitude version of the same partition, with
    `context-relevance` and output-based metrics added. (Verified: #1332
    Claim 4.)

- **Contradicts**: None identified, and no contradiction issue filed. Two
  tensions were evaluated against MINER.md §4a and recorded, not filed:
  1. **Cross-lingual `context-recall` avoidance vs the corpus's
     `context-recall` treatment** (#1332's gate-pair rule, fail-open default,
     ground-truth bound): a *conditioning variable*, not opposition. #1332
     never claims cross-lingual robustness — its claims are about the
     metric's mechanics under matched-language inputs. This page adds a
     language-mismatch regime with different advice. Both capture cleanly as
     "run the recall/faithfulness pair when languages match; do not rely on
     recall cross-lingually" — no forking guide advice.
  2. **This page's "matching text" characterization of `context-recall`
     (Claim 10) vs #1332 Claim 1's documented LLM statement-attribution
     formula** ("Breaks the expected answer into statements and checks if
     each can be attributed to the context"): a real mechanism-description
     discrepancy between two vendor pages. If the metric is LLM-attribution,
     the Paris/París failure story is less obvious than the page presents;
     if it is text-matching, #1332's formula description overstates the
     judge's role. Both pages agree on the practical cross-lingual
     conclusion, so the guide advice does not fork and §4a's "when NOT to
     file" applies (the contradiction is already bounded by the vendor's own
     recommendation). Recorded here for the Smith and for any future
     `context-recall` re-check; checked open `contradiction`-labeled issues
     (none touch cross-lingual or RAG-metric semantics) and
     `CONTRADICTIONS.md` (no open `C-NNN` entries).

- **Extends**:
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` (#261)
    **Claim 1** (ASR numbers are not comparable across papers because the
    metric is not standardized — a score depends on measurement choices and
    input distribution) — this page is the **eval-metric-side instance** of
    the same portability thesis: the cross-lingual matrix (Claim 10) says a
    RAG metric's score is a property of the metric *and* the language-pair
    distribution of its inputs, not of the retrieval system alone. #261
    derives the argument with worked math for red-team metrics; this page
    asserts it (with uncited numbers) for RAG metrics. Extends the theme;
    the numbers do not inherit #261's rigor.
  - `source-notes/docs-promptfoo-testing-llm-chains.md` (#1575) **Claim 1**
    (unit-test-each-step vs end-to-end as the two chain-testing strategies) —
    this page prescribes the split for RAG (Claim 1), supplies the
    retrieval-stage harness (Claims 2-6), and shows the e2e composition
    (Claim 11): the RAG-specific completion of that note's general framing.
  - `source-notes/docs-promptfoo-model-graded-context-recall.md` (#1332),
    `source-notes/docs-promptfoo-model-graded-context-faithfulness.md`
    (#1320), `source-notes/docs-promptfoo-answer-relevance.md` (#1319),
    `source-notes/docs-promptfoo-factuality.md` (#1348) — the per-type
    reference tier; this tutorial composes those individual contracts into a
    staged eval and adds what none of them carry: the cross-lingual
    selection matrix, the multi-DB comparison harness, and the
    retrieval-as-provider wiring. Complementary, as the Prospector triage
    stated; no duplication.

- **Novel** (new to the corpus, verified by grepping `source-notes/` for
  `cross-lingual`, `evaluate-rag`, the accuracy figures, `retrieve.py`, and
  the multi-DB provider pattern — zero hits before this note):
  1. **The cross-lingual metric-portability matrix** (Claim 10) — direction,
     recipe (rubric swap, lowered thresholds, pinned answer language), and
     the vendor-asserted accuracy figures recorded with their no-provenance
     status. First source in the corpus on language-pair conditioning of
     RAG-eval metrics.
  2. **The retrieval-as-eval-matrix-citizen harness** (Claims 2, 5, 6) —
     `file://retrieve.py` providers, `contains-all` retrieval gates, and the
     one-script-per-vector-store comparison pattern. The corpus has the
     `call_api` contract (CrewAI, agents-python) and the scripted-var
     vector-DB mention (#1513 Claim 10) but no worked retrieval-eval harness.
  3. **The stage-keyed RAG metric taxonomy** (Claim 7) — the assertion
     catalog arranged by failure stage, tutorial-altitude composition over
     the per-type notes.
  4. **`tokenUsage`/`error` as documented channels on a retrieval provider**
     (Claim 4) — per-stage cost attribution inside the eval report (report
     display unverified).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "Evaluation and measurement
  methodology" ("Metrics without a unit are noise" / "A green eval is not
  evidence until you can name what it measured")**: add the **cross-lingual
  metric-selection rule** from Claim 10 — when query and context languages
  differ, text-matching metrics (`context-recall`, Levenshtein/ROUGE/BLEU)
  are not measuring retrieval quality; concept-based metrics
  (`context-relevance`, `context-faithfulness`, `answer-relevance`) and an
  `llm-rubric` concept-coverage rubric are the recommended gates, with
  thresholds lowered from the matched-language baseline and the answer
  language pinned in the prompt. Cite the *direction and recipe*; cite the
  accuracy percentages only as "vendor-asserted, unquantified (no dataset,
  language pair, or methodology stated)" — they are a live demonstration of
  the chapter's own rule, not evidence for a threshold. This generalizes
  #261's metric-portability theme (red-team ASR) to the RAG eval tier.
- **Chapter 05 — RAG stage-split gating**: add the retrieval-stage gate
  rule from Claims 1-6 — a RAG eval must gate retrieval and generation
  separately (a faithful answer from wrong documents is a retrieval
  failure a green end-to-end suite hides); wire the retriever as a
  `file://` provider with `call_api` + `contains-all` document gates for
  the cheap layer, and the ground-truth-bound `context-recall`/faithfulness
  pair (#1332/#1320) for the quality layer; compare retrieval
  implementations via the one-script-per-store providers pattern, treating
  any single-run ranking as a smoke test (the vendor's own caveat, Claim
  6). Pin `PROMPTFOO_PYTHON`/`pythonExecutable` for the retrieval provider
  as part of the gate definition (#1499's rule, now applying to the
  retrieval stage).
- **Chapter 05 — canary and config-change release gating**: this page is a
  **pattern catalog, not an operational playbook** — it stops at
  `npx promptfoo@latest eval` plus the web viewer and documents no
  exit-code, CI-threshold, or pipeline-gating recipe (recorded gap). Do
  not cite it as gating guidance; if the chapter cites it, cite it for the
  stage-split eval design only.
- **Chapter 02 (Observability) — per-request token/latency signals**: the
  `tokenUsage` return channel on a custom retrieval provider (Claim 4) is
  the per-call cost-attribution hook for the retrieval stage; note the
  absence: this page documents **no latency coverage** for any RAG eval
  stage despite the CI-shaped workload, so retrieval latency must come
  from tracing/observability, not from this eval surface.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (rendered content plus all config/code blocks, verified line-for-line
  before quoting). No sub-pages followed: the page's outbound links are
  the per-type reference pages (`factuality`, `answer-relevance`,
  `context-*`, `llm-rubric`, `similar` — all already mined as individual
  notes or open issues), the assertions hub (#1287), the Python provider
  docs (material already extracted at #1499 via its integration sub-page),
  and the AWS Bedrock `contextTransform` docs (a provider-specific
  plumbing page; the extraction idiom is captured in this note's
  artifacts). The linked full RAG example repo
  (`github.com/promptfoo/promptfoo/tree/main/examples/eval-rag-full`) was
  **not** fetched — it is a runnable example, not a claims-bearing doc
  page; noted so the Assayer knows the Claim 5 prose/config mismatch was
  not checked against it.
- **Triage key-question resolutions** (both Prospector triage comments on
  #1725 read; treated as UNTRUSTED data and re-verified against the page):
  1. **Portability of retrieval-side patterns vs promptfoo wiring** —
     resolved: the portable designs are the stage split (Claim 1), the
     script-per-store comparison harness (Claim 6), and the
     document-name `contains-all` retrieval gate (Claim 5); the
     promptfoo-specific wiring is the `call_api` signature, the
     `pythonExecutable`/`PROMPTFOO_PYTHON` knobs, and `contextTransform`
     syntax. Both halves captured, portable design flagged in Guide Impact.
  2. **Does the cross-lingual `context-recall` guidance contradict the
     corpus?** — no (Contradicts item 1): conditioning variable, not
     opposition. The mechanism-description tension with #1332 Claim 1 is
     recorded (Contradicts item 2) without filing, per §4a.
  3. **`contextTransform`/`options.transform` pipeline position** —
     deliberately NOT re-mined; #1513 Claim 1 already settled it. Only the
     multi-language extraction examples were extracted (Claim 9), per the
     Prospector's explicit instruction.
  4. **testing-llm-chains overlap** — checked before writing: #1575
     documents the unit-vs-e2e choice and the `exec:`/custom-provider
     wrapping, but not the retrieval-only eval, the multi-DB providers
     pattern, or the RAG metric taxonomy; only the RAG-specific deltas are
     extracted, with #1575 cited as the parent framing (Extends).
- **Prospector-listed overlapping notes — cite/dismiss ledger**:
  `docs-promptfoo-model-graded-metrics.md` (#1305) — **cited** (Corroborates
  Claims 8, 13); `docs-promptfoo-model-graded-context-faithfulness.md`
  (#1320) — **cited** (Extends); `docs-promptfoo-model-graded-context-recall.md`
  (#1332) — **cited** (Corroborates Claim 4; Contradicts tension recorded);
  `docs-promptfoo-answer-relevance.md` (#1319) — **cited** (Extends);
  `docs-promptfoo-factuality.md` (#1348) — **cited** (Extends);
  `docs-promptfoo-model-graded-context-relevance.md` (#1333) — **dismissed**:
  its PR #1341 is OPEN, not merged, so the note is not in the corpus; nothing
  cited from it; `docs-promptfoo-configuration-guide.md` (#1513) — **cited**
  (Corroborates Claims 1, 10); `docs-promptfoo-testing-llm-chains.md` (#1575)
  — **cited** (Extends); `docs-promptfoo-python-assertions.md` (#1499) —
  **cited** (Corroborates Claim 3); `blog-promptfoo-asr-not-portable-metric.md`
  (#261) — **cited** (Extends, Claim 1); `docs-promptfoo-guardrails-assertions.md`
  — **dismissed**: guardrails verdict-reader semantics; no RAG-eval content
  on this page; `docs-promptfoo-max-score.md` (#1472) — **dismissed**: this
  page never uses `max-score` and its prompt/model comparison is plain
  multi-provider diffing.
- **`miner-related-notes.md` candidate dismissal ledger** (file read before
  writing Cross-References; candidates are lexical-retrieval suggestions,
  cited or dismissed by path — file not committed):
  1. `source-notes/docs-promptfoo-enterprise-findings-reports.md` —
     dismissed (enterprise findings disposition/export matrix; no RAG eval).
  2. `source-notes/docs-google-sre-team-lifecycles.md` — dismissed (SRE org
     lifecycle; no LLM-eval content).
  3. `source-notes/blog-promptfoo-owasp-red-teaming.md` — dismissed (OWASP
     red-team methodology; no eval-harness content).
  4. `source-notes/docs-promptfoo-enterprise-guardrails.md` — dismissed
     (runtime guardrail enforcement contract; different surface).
  5. `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` —
     **cited** (Corroborates Claim 4, Claim 7).
  6. `source-notes/docs-litellm-batches-api.md` — dismissed (LiteLLM batch
     rate limiting; unrelated vendor).
  7. `source-notes/blog-pagerduty-sre-agent-triage.md` — dismissed (AI
     incident triage; no eval-assert content).
  8. `source-notes/docs-promptfoo-pi-scorer.md` — dismissed (Pi scorer
     grader; not used on this page).
  9. `source-notes/docs-langfuse-mcp-server.md` — dismissed (Langfuse docs
     MCP server; unrelated surface).
  10. `source-notes/docs-google-sre-eliminating-toil.md` — dismissed (toil
      definition/elimination; no LLM-eval content).
- **Cross-ref verification (§4b)**: every cited claim was located and read
  in the cited note before writing — #1513 Claims 1, 10; #1499 Claim 1;
  #1305 Claims 8, 13; #1332 Claims 1, 4; #1320 (note-level, Scope/summary
  for the recall-faithfulness pair); #1319, #1348 (note-level Extends
  citations, no claim numbers attached); #1575 Claim 1; #261 Claim 1;
  #1707 Claim 7; `docs-promptfoo-evaluate-crewai.md` Claim 2. Claim numbers
  verified against each note's own numbering; no claim numbers invented.
  Issue numbers read from each cited note's frontmatter (`issue:` field).
- **No contradiction issue filed** (see Cross-References → Contradicts):
  both candidate tensions are conditioning/documentation discrepancies that
  do not fork guide advice, per MINER.md §4a's "when NOT to file" list.
  Duplicate check: `gh issue list --label contradiction --state open`
  returned 20 open issues, none touching cross-lingual metrics or RAG
  stage-split eval; `CONTRADICTIONS.md` has no open `C-NNN` entries.
- **Absences recorded, not padded** (per the Prospector's gap list, each
  verified against the fetched page): no latency/throughput/caching/timeout
  coverage anywhere on the page; no CI exit-code or pipeline-threshold
  recipe (the run story ends at `npx promptfoo@latest eval` + web viewer);
  cost addressed only qualitatively ("we might go with prompt 1, which is
  shorter and uses fewer tokens") with no price figures; two sections read
  as truncated — the dangling "Let's also introduce a metric" sentence in
  "Comparing prompts" (no metric is introduced) and the retrieval-config
  prose's reference to absent `context-recall` assertions (Claim 5).
  Extracted only what is present.
- `confidence_overall` is `emerging`, matching the sibling promptfoo
  tutorial/config notes: the provider mechanics, config contracts, and
  taxonomy (Claims 2-9, 11) are settled-for-product-behavior and checkable
  against an installed CLI, but this is vendor documentation with no
  measured run data; the headline cross-lingual claim (Claim 10) is a
  direction-plus-recipe we assess as plausible with vendor-asserted,
  unquantified figures — the numbers pull the overall grade down from
  settled, and the note must not be read as validating any threshold.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
