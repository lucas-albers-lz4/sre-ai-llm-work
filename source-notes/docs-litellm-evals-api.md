---
source_url: https://docs.litellm.ai/docs/evals_api
source_type: docs
title: "/evals — LiteLLM AI Gateway Documentation (OpenAI Evaluations API served by the proxy)"
author: "LiteLLM (BerriAI) — official vendor documentation"
date_published: unknown (living vendor docs; page front-matter last_updated 2026-10-20)
date_extracted: 2026-10-22
last_checked: 2026-10-22
status: current
confidence_overall: settled
issue: "#1691"
---

# /evals (LiteLLM Docs)

> LiteLLM's `/docs/evals_api` page documents the gateway's implementation of
> OpenAI's Evaluations API: evals are **server-side objects** (create / list /
> retrieve / update / delete), the eval corpus is the proxy's own **stored
> completions** selected by request `metadata`, the grader is a **categorical
> label model** (`label_model` + `passing_labels`) whose prompt is templated
> over `{{item.input}}` / `{{sample.output_text}}`, and a run reports four
> counters — `total`, `passed`, `failed`, **`errored`** — plus per-criterion
> `average_score` and a `report_url`. The page's real contribution to the guide
> is what it *does not* say: there is no authorization model, no rate limit,
> no spend attribution, no retention contract, no concurrency bound, no error
> body, and no `status` state machine anywhere on it — while the schema it does
> publish contains two sharp operational traps (a criterion contract that
> cannot be updated, and run results that are destructible).

## Source Context

- **Type**: docs (official vendor documentation — LiteLLM AI Gateway, living
  Docusaurus page under "Supported Endpoints → /evals"; the canonical raw
  markdown is served at `https://docs.litellm.ai/docs/evals_api.md`, whose
  front matter carries `last_updated: "2026-10-20"`). The page is a **leaf**:
  its `related:` list names `/docs/proxy/managed_finetuning` and
  `/docs/generateContent`, and both of those pages link *to* `/evals` in their
  own `related:`/navigation lists without containing any eval content (checked
  2026-10-22: 2 matches each, both navigation links). There are no
  sub-pages.
- **Author credibility**: LiteLLM (BerriAI) first-party product documentation.
  Authoritative for the *surface* — which endpoints exist, the request/response
  shapes, the criterion and data-source contracts, the result counters, the
  pagination fields, the deletion semantics. Per the Prospector's bounding
  rule, documented **product behavior and schema/contract claims are recorded
  as `settled`**: the page carries no benchmark, no effectiveness claim, and no
  operational guidance, and none is inferred here.
- **Scope**: Covers the eval CRUD surface, the run CRUD surface, the
  `label_model` criterion shape with its `{{item.input}}` /
  `{{sample.output_text}}` templating, the two data-source forms
  (`stored_completions` and `completions` + `input_messages` +
  `item_reference`), the run-result counters, the pagination fields, and the
  per-eval credential note. Does **not** cover (and the page is silent on):
  authorization / tenancy / virtual-key scoping, rate limits, quotas,
  concurrency and grader fan-out, stored-completion retention, cost and spend
  attribution, error codes and retry behavior, idempotency, the `status`
  state machine, the contents and lifetime of `report_url`, and how a stored
  completion is written in the first place. These are recorded as OQ-1 … OQ-9
  below, not as findings.
- **Adjacent pages consulted for gap-checking** (2026-10-22, per MINER §1;
  not extracted as claims about `/evals`): `/docs/proxy/cost_tracking`
  (Spend Tracking) and `/docs/proxy/logging` (AI Gateway — Logging &
  Observability). Both were checked for `/evals` and `stored_completions`
  coverage: neither mentions them. The Spend Tracking page's own walkthrough is
  "`/chat/completions`"-shaped and its only mention of an eval product is the
  `deepeval` callback in the Logging page (an external eval-framework
  integration, unrelated to the `/evals` endpoints). The consequence is
  recorded in Claim 8.

## Extracted Claims

### Claim 1: The proxy serves OpenAI's Evaluations API as managed, server-side state — the full CRUD surface `client.evals.create / list / retrieve / update / delete` — so an evaluation definition lives in the gateway, addressed by `eval_id`, not in client code
- **Evidence**: The page intro plus the five `Evaluation Management`
  subsections, each with its own SDK snippet (`create` at "Example: Sentiment
  Classification Eval", `list` at `List Evaluations`, `retrieve` at `Get a
  Specific Evaluation`, `update` at `Update an Evaluation`, `delete` at
  `Delete an Evaluation`).
- **Confidence**: settled (documented endpoint inventory)
- **Quote**: "LiteLLM Proxy supports OpenAI's Evaluations (Evals) API, allowing you to create, manage, and run evaluations to measure model performance against defined testing criteria." / "Create an evaluation with testing criteria and data source configuration." / "Permanently delete an evaluation."
- **Our assessment**: The architectural fact that matters for the guide: an
  eval is now *gateway state* with a lifecycle (create → many runs → delete),
  not a script in a CI job. Two consequences follow immediately and neither is
  documented on the page: (a) evaluation definitions become shared state that
  needs ownership, versioning, and a lifecycle policy — and the page's update
  path cannot express a rubric change at all (Claim 10), so "version the
  rubric" has no API; (b) the objects outlive the process that created them, so
  the page's silence on who may list, read, and delete them (Claim 8) is a
  real tenancy question for a shared proxy, not a nitpick.

### Claim 2: The eval corpus is the proxy's own **stored completions**, selected by request `metadata` — and the filter appears at *two* levels: the eval's broad `data_source_config` and the run's narrower `data_source.source`
- **Evidence**: The create snippet's `data_source_config={"type": "stored_completions", "metadata": {...}}`; the second example's `data_source_config` with `{"usecase": "push_notifications_summarizer"}`; the run snippet's `data_source={"type": "completions", "source": {"type": "stored_completions", "metadata": {"prompt_version": "v1"}}}}`.
- **Confidence**: settled for the two shapes; the *composition* rule between
  the eval-level and run-level filters is undocumented (OQ-1)
- **Quote** (from `Create an Evaluation` / `Example: Sentiment Classification Eval`): `"type": "stored_completions",` / `"metadata": {"usecase": "chatbot"}` / (from `Example: Push Notifications Summarizer Monitoring`) `"metadata": {` / `"usecase": "push_notifications_summarizer"` / (from `Create a Run` → `Using Stored Completions`) `"type": "completions",` / `"source": {` / `"type": "stored_completions",` / `"metadata": {` / `"prompt_version": "v1",`
- **Our assessment**: This is the concrete instantiation of "eval the traffic
  you actually serve" that the triage asked about — with one qualification the
  page never states: **the corpus is not automatically production traffic.**
  It is whatever the proxy happened to store under the metadata keys the caller
  chose, and the page's own workflow *generates* its corpus by issuing chat
  completions through the proxy with `metadata` tags (Claim 11). The surface
  supplies the *retrieval* half of the pattern (filter stored completions by
  metadata), never the *instrumentation* half (tag live traffic at request
  time). Compare the corpus's production-eval primitive, where a Rule selects
  live observations with filters *and a sampling rate*
  (`docs-langfuse-evaluate-production-traffic`, Claim 1): there is no sampling
  knob and no cost preview here. Also note the undocumented composition: the
  examples imply the run's `prompt_version` filter *narrows* the eval's
  `usecase` filter, but whether a run filter replaces or intersects the eval
  filter is nowhere stated (OQ-1) — a team with two eval objects overlapping
  on metadata has no documented way to reason about which rows a run grades.

### Claim 3: The pass/fail contract is a **categorical label classifier**, not a score — a criterion is `{type: "label_model", model, input, passing_labels, labels, name}`, the grader emits one of `labels`, and the item passes when that label is in `passing_labels`
- **Evidence**: The `Sentiment Classification Eval` criterion and the
  "Push Notification Summary Grader" criterion, both reproduced verbatim in
  Concrete Artifacts.
- **Confidence**: settled (documented criterion schema)
- **Quote**: `"type": "label_model",` / `"model": "gpt-6-luna",` / `"passing_labels": ["positive"],` / `"labels": ["positive", "neutral", "negative"],` / `"passing_labels": ["correct"],` / `"labels": ["correct", "incorrect"],`
- **Our assessment**: The gate is a closed-label classifier, so there is no
  rubric scale, no numeric threshold, and no partial credit in the criterion
  itself; the only numeric field in the whole surface (`average_score`) appears
  in the run *results* (Claim 6), never in the pass/fail rule. That pins
  LiteLLM's judge to the categorical variant of LLM-as-a-judge, and it makes
  one failure mode structural rather than incidental: a grader response that
  is none of the declared labels (a refusal, a truncated answer, a parse
  failure) has no documented home — it is exactly the case the `errored`
  bucket would need to absorb, and the page never says what fills that bucket
  (Claim 6, OQ-2). The corpus already teaches the discipline this surface
  needs: grader errors must be excluded from pass/fail accounting and reported
  separately (`docs-promptfoo-llm-as-a-judge`, Claim 2).

### Claim 4: Grader prompts are templated over the stored completion with `{{item.input}}` and `{{sample.output_text}}` in a two-role (`developer` + `user`) message array — so the grader is a **second model call whose prompt embeds production content**
- **Evidence**: The two prompt constants in the `Push Notifications Summarizer
  Monitoring` example and the `{{item.input}}` placeholder in the sentiment
  criterion.
- **Confidence**: settled (documented template vocabulary and message shape)
- **Quote**: `"content": "Statement: {{item.input}}"` / (from the example's constants)
  ```
  Push notifications: {{item.input}}
  Summary: {{sample.output_text}}
  ```
- **Our assessment**: The hermeticity and cost shape of the whole feature:
  every graded item produces a grader call whose prompt carries the original
  user content *and* the subject model's output, sent to a **different**
  model (`testing_criteria[].model`). Two things follow that the page does not
  address: (a) grader fan-out is a second billable stream whose cost, limits,
  and concurrency are undocumented (OQ-3) — the corpus has a precedent for
  what the *good* version of this looks like, where the vendor splits a second
  sub-inference's spend out of the top-level `usage` object
  (`docs-litellm-anthropic-advisor-tool`, Claim 2); (b) the grader prompt is
  a **data-egress path**: content the subject model already saw is shipped to
  the grader model, which may sit on a different provider — a Ch06-grade
  cross-provider data-flow fact stated nowhere on the page. The placeholder
  vocabulary is also undocumented beyond these two names (OQ-4): the page never
  lists the available template variables, so a team cannot know whether e.g.
  the stored completion's model or metadata is addressable.

### Claim 5: Grader model and subject model are separate fields, and the page's own example ships a **name/model mismatch** — the criterion grades with `gpt-6-luna` while the run evaluates `gpt-6.1-sol`, and the run names are `f"gpt-5.6-terra-run-{prompt_version}"`
- **Evidence**: The `Using Completions with Different Models` snippet, read
  against the criterion's `model` field in the same example.
- **Confidence**: settled (both fields and the literal values are published
  in the same snippet set)
- **Quote**: `"model": "gpt-6.1-sol",` / `name=f"gpt-5.6-terra-run-{prompt_version}",` / `"model": "gpt-6-luna",`
- **Our assessment**: Two contracts in one example. `data_source.model` is the
  **subject** model; `testing_criteria[].model` is the **grader**. Nothing on
  the page couples them, so a team can — and the vendor's own snippet does —
  grade one model's output with a different model. That is desirable
  hermeticity (the grader is not contaminated by the subject), but it also
  makes the grader an independent, unpinned variable with no documented
  version/grader-drift handling. The operational trap is the naming: `name` is
  a free-text label (the other examples use `"v1-run"` and `"v2-run"`, i.e.
  prompt-version labels), so a dashboard or alert keyed on run names will
  mis-report which model regressed — the example's runs are *called*
  `gpt-5.6-terra-run-*` while the model actually evaluated is `gpt-6.1-sol`.
  Worse, run names cannot be corrected afterwards: no `runs.update` is
  documented (Claim 10), so a mislabeled run can only be deleted — losing the
  artifact in order to fix the label.

### Claim 6: The run result model separates four counters — `total`, `passed`, `failed`, **`errored`** — at the run level, and again per criterion (`per_testing_criteria_results[].result_counts` plus `average_score`); the `errored` bucket is the surface that would keep infrastructure failures out of quality failures, but the page never defines it
- **Evidence**: The `Get Run Details` snippet (run-level counters and the
  per-criteria loop) and the `List Runs` snippet (the pass-rate idiom).
- **Confidence**: settled that the four counters and the per-criteria result
  object exist; the **semantics** of `errored`, the relation between the
  counters, and the scale of `average_score` are undocumented (OQ-2)
- **Quote** (from `Get Run Details`):
  ```
      print(f"Total: {run.result_counts.total}")
      print(f"Passed: {run.result_counts.passed}")
      print(f"Failed: {run.result_counts.failed}")
      print(f"Error: {run.result_counts.errored}")
  ```
  / (same snippet, per-criteria loop):
  ```
          print(f"\nCriteria {criteria_result.testing_criteria_index}:")
          print(f"  Passed: {criteria_result.result_counts.passed}")
          print(f"  Average Score: {criteria_result.average_score}")
  ```
- **Our assessment**: This is the answer to the triage's central question,
  and the answer is *half* a contract. The schema is the right shape — a
  fourth bucket that can hold harness/infrastructure failures separately from
  genuine quality failures — and the corpus's judge discipline says exactly
  that separation is required (`docs-promptfoo-llm-as-a-judge`, Claim 2: a
  grader error must not be counted as a failure of the system under test). But
  the page defines nothing: not what produces `errored` (grader call failure?
  an unparseable label? a timeout?), not whether errored items are included
  in `total`, not whether `passed + failed + errored == total`, and not the
  scale of `average_score` (the criterion is categorical, so the scale is
  undefined by the page). And the page's *own* reporting idiom throws the
  distinction away:
  ```
          print(f"Results: {run.result_counts.passed}/{run.result_counts.total} passed")
  ```
  — a grader outage that increments `errored` surfaces as a lower pass rate,
  i.e. infrastructure noise rendered as a quality regression. The schema is
  right and the documentation's own quickstart is the trap. Note also the
  asymmetry with the rest of the LiteLLM corpus: this failure class has **no
  HTTP signal at all** — it lives inside a result payload of an otherwise
  successful call — whereas the agent path's cost-cap failure surfaces as a
  429 (`docs-litellm-a2a-iteration-budgets`, Claim 5).

### Claim 7: Run lifecycle is exposed as exactly four fields — `status`, `started_at`, `completed_at`, `report_url` — the page prints `status` but never enumerates its values, and `report_url` is the only pointer to a per-run artifact
- **Evidence**: The `Create a Run` snippet (`status`, `report_url`), the
  `List Runs` snippet (`status`), and the `Get Run Details` snippet
  (`status`, `started_at`, `completed_at`).
- **Confidence**: settled that these fields exist; the status state machine,
  terminality, polling guidance, and timeout are undocumented (OQ-5)
- **Quote**: `print(f"Status: {eval_run_result.status}")` / `print(f"Report URL: {eval_run_result.report_url}")` / `print(f"Started: {run.started_at}")` / `print(f"Completed: {run.completed_at}")`
- **Our assessment**: Four fields, zero semantics. No list of status values, no
  statement of which are terminal, no polling interval, no timeout, and no
  distinct error state — so a caller must treat `status` as opaque and cannot
  build a completion gate without a timeout heuristic; the only completion
  signal available is a non-null `completed_at`, and even that equivalence is
  not stated on the page. `report_url` is the interesting field: it is the
  *only* pointer to a human-readable artifact, because no per-item results are
  documented anywhere — `evals.runs.retrieve` returns counters, not the graded
  items. So the artifact for an audit trail is a URL whose contents,
  authentication requirement, and lifetime are undocumented (OQ-6): a report
  URL that is unauthenticated is a data leak, and one that requires the proxy
  key cannot be handed to a non-engineering reader. The guide's compliance
  rule needs an explicit answer here, which the page does not give.

### Claim 8: The page documents **no** authorization, tenancy, rate limit, quota, concurrency, retention, spend, cost, retry, or error contract for the evals surface — the only tenancy statement on the whole page is a code comment about per-eval model credentials
- **Evidence**: The comment at the end of the `Sentiment Classification Eval`
  snippet; the `List Evaluations` snippet (whose only parameters are `limit`,
  `order`, `after` — no key, team, or owner filter); and the absence of any
  such content across every section of the page.
- **Confidence**: settled (a documented absence, verified section by section)
- **Quote**: "# Note: If you want to use model-specific credentials for this evaluation, you can specify the model name in the extra body parameters." / (from `List Evaluations`) `evals_response = client.evals.list(` / `limit=20,` / `order="desc"` / `)`
- **Our assessment**: The absence is the finding, and it is unusually complete
  for a vendor endpoint page. A reader cannot learn: who may create, read, or
  delete an eval; whether `evals.list` is scoped to the caller at all (the
  snippet takes no ownership filter, so in a shared proxy the eval catalogue is
  enumerable by anyone who can list — and the corpus has already mapped that
  authorization resolution is *per-surface* and asymmetric, MCP resolving six
  levels against A2A's two, `docs-litellm-gateway-auth-reference` Claim 7, so
  the page answering nothing is a third depth, not a global gap); whether eval runs or
  grader calls consume the caller's rate limits, virtual-key budget, or spend
  (compare the agent path, where the budget semantics *are* documented,
  `docs-litellm-a2a-iteration-budgets` Claim 4); what error body or status a
  rejected create returns; whether stored completions are retained and for how
  long (the whole feature depends on it); and what happens when the grader
  model 429s mid-run. The credential comment is itself under-specified —
  "specify the model name in the extra body parameters" does not say where the
  credential comes from, who it is scoped to, or whether it is persisted *with
  the eval*; if it is, the eval object holds a secret, which is a Ch06
  question the page leaves open (OQ-7). Finally, and checkably: the gateway's
  own Spend Tracking page (`/docs/proxy/cost_tracking`, consulted
  2026-10-22) contains no occurrence of `/evals` or `stored_completions` and
  its step-by-step walkthrough sends only a `/chat/completions` request; the
  Logging page
  (`/docs/proxy/logging`, consulted 2026-10-22) likewise contains no `/evals`
  or `stored_completions` — its only eval-related match is the `deepeval`
  callback. So *nothing in the documentation* says eval traffic is logged,
  metered, or attributed to a key.

### Claim 9: Pagination is cursor-based — `limit`, `order`, `after`, plus the response fields `has_more` and `last_id` — and the documented idiom is to fetch the next page with `after=last_id` once `has_more` is set
- **Evidence**: The `List Evaluations` snippet, which is the only pagination
  example on the page.
- **Confidence**: settled (documented pagination contract; the allowed values
  of `order` and the maximum page size are undocumented — OQ-8)
- **Quote**:
  ```
  if evals_response.has_more:
      # Fetch next page
      next_evals = client.evals.list(
          after=evals_response.last_id,
          limit=20
      )
  ```
- **Our assessment**: `last_id` is a *cursor*, and the field name is the
  trap: a caller who reads it as the id of the last eval returned and then
  calls `evals.retrieve(last_id)` gets the wrong object — and
  `evals.update(last_id, ...)` or `evals.delete(last_id)` would target an
  arbitrary eval, which is a plausible accidental-deletion path on a surface
  whose delete is permanent (Claim 10). `order="desc"` appears with no
  enumeration of allowed values and no stated default; `limit=20` is an
  example, not a documented maximum. And because the page documents no
  server-side filter on the list surface, listing every eval on this proxy is
  the only documented behaviour available to a caller — an inventory/tenancy
  question (Claim 8).

### Claim 10: Deletion is permanent and the mutation paths are narrow — an eval can be updated for `name` and `metadata` **only**, a run cannot be updated at all, and deleting a run deletes its results
- **Evidence**: The `Update an Evaluation` snippet (the only two fields
  passed), the `Delete an Evaluation` snippet, the `Delete a Run` snippet and
  its prose, and the absence of any `runs.update` endpoint across the page.
- **Confidence**: settled (documented update/delete surface)
- **Quote**: "Update evaluation metadata or name." / "Permanently delete a run and its results." / `print(f"Deleted: {delete_response.deleted}")  # True` / `print(f"Run ID: {delete_response.run_id}")`
- **Our assessment**: Two consequences with real operational teeth. (a) **The
  grader contract is immutable**: neither `testing_criteria` nor
  `data_source_config` appears in the documented update surface, so changing
  a rubric or a corpus filter means creating a *new* eval and re-pointing the
  workflow — which fragments run history across eval IDs and makes "has this
  rubric ever passed?" unanswerable from the API. For a prompt-regression gate
  this is the single most consequential property on the page, and the page
  never states it. (b) **The evidence is destructible**: deleting a run
  deletes its results, and `report_url` is the only artifact pointer
  (Claim 7) — so the guide's rule that eval output *is* compliance evidence
  (`guide/06-security-and-trust.md:471`) needs an explicit
  export-before-delete step that no page in this corpus documents. (c) A
  mislabeled run cannot be renamed (Claim 5), only deleted — losing the
  artifact in order to fix the label.

### Claim 11: The page's own framing of the feature is **prompt-regression monitoring over stored completions** — the corpus is generated by replaying two prompt versions through the proxy's chat-completions path with `metadata` tags, then graded per version
- **Evidence**: The `Push Notifications Summarizer Monitoring` prose, the
  corpus-generation snippet, and the two run-creation snippets that filter on
  `prompt_version`.
- **Confidence**: settled (documented workflow)
- **Quote**: "This example shows how to monitor prompt changes for regressions in a push notifications summarizer:" / "First, generate some test data by making chat completions with metadata:" / (from the corpus-generation snippet)
  ```
              metadata={
                  "prompt_version": version,
                  "usecase": "push_notifications_summarizer"
              }
  ```
  / "Now create runs to evaluate different prompt versions:"
- **Our assessment**: This is the use case the vendor wants a team to copy: a
  versioned A/B over a pinned corpus — same inputs, two prompts, one grader.
  The operational caveat is what the page does not say about where the corpus
  comes from. The corpus items are created by the team's *own* completion
  calls, so an eval corpus is by construction a set of stored request/response
  bodies; the corpus-generation calls consume the gateway's rate limits,
  budget, and spend like any other traffic, and their content is added to the
  proxy's stored-completions pool with no documented retention or deletion
  path (OQ-9). If a team reuses one metadata namespace for real traffic and
  for fixtures, the eval corpus becomes a copy of production user content,
  and the page never warns about that or offers a way to remove stored
  completions. Note the consequence for the guide's coverage rule: an eval
  built this way measures the *fixtures the team chose*, and the page offers
  no mechanism to reach traffic the team did not deliberately tag.

### Claim 12: The `input_messages` / `item_reference` variant lets a run re-execute a **different subject model over the same stored inputs** — the model-comparison mechanism, whose subject semantics the page leaves ambiguous
- **Evidence**: The `Using Completions with Different Models` snippet and its
  one-line prose.
- **Confidence**: settled for the schema; the semantics of `item.input` and
  whether the stored completion's *output* or only its *input* is re-used are
  undocumented (OQ-4)
- **Quote**: "Test how different models perform on the same inputs:" /
  ```
              "input_messages": {
                  "type": "item_reference",
                  "item_reference": "item.input",
              },
              "model": "gpt-6.1-sol",
  ```
- **Our assessment**: This is the hermetic-comparison primitive: pin the
  inputs, vary the model, keep the grader — the shape a model-migration gate
  needs, and the clearest statement of intent on the entire page ("Test how
  different models perform on the same inputs"). It also depends entirely on
  stored completions retaining the original input messages, which the page
  never states and never bounds with a retention window. The ambiguity worth
  flagging: `source` is still `{"type": "stored_completions", ...}` while
  `model` names a subject model, so the page supports two readings — the
  stored completion's *output* is the artifact being graded, or the stored
  completion's *inputs* are re-run through `model` and the fresh output is
  graded — and the two readings give different verdicts. An eval whose
  subject semantics are ambiguous is not a regression gate, and the page gives
  a reader nothing to disambiguate with.

## Concrete Artifacts

All artifacts verbatim from the page's raw markdown
(`https://docs.litellm.ai/docs/evals_api.md`, `last_updated: "2026-10-20"`,
fetched 2026-10-22).

### Eval creation with a `label_model` grader (from `Example: Sentiment Classification Eval`)

```python
eval_obj = client.evals.create(
    name="Sentiment Classification",
    data_source_config={
        "type": "stored_completions",
        "metadata": {"usecase": "chatbot"}
    },
    testing_criteria=[
        {
            "type": "label_model",
            "model": "gpt-6-luna",
            "input": [
                {
                    "role": "developer",
                    "content": "Classify the sentiment of the following statement as one of 'positive', 'neutral', or 'negative'"
                },
                {
                    "role": "user",
                    "content": "Statement: {{item.input}}"
                }
            ],
            "passing_labels": ["positive"],
            "labels": ["positive", "neutral", "negative"],
            "name": "Sentiment Grader"
        }
    ]
)

# Note: If you want to use model-specific credentials for this evaluation, you can specify the model name in the extra body parameters.
```

### Grader prompt template with the two documented placeholders (from `Example: Push Notifications Summarizer Monitoring`)

```python
GRADER_DEVELOPER_PROMPT = """
Label the following push notification summary as either correct or incorrect.
The push notification and the summary will be provided below.
A good push notification summary is concise and snappy.
If it is good, then label it as correct, if not, then incorrect.
"""

GRADER_TEMPLATE_PROMPT = """
Push notifications: {{item.input}}
Summary: {{sample.output_text}}
"""
```

### Corpus generation with `metadata` tags (from `Create a Run` → `Using Stored Completions`)

```python
        tasks.append(client.chat.completions.create(
            model="gpt-6-luna",
            messages=[
                {"role": "developer", "content": prompt},
                {"role": "user", "content": notifications},
            ],
            metadata={
                "prompt_version": version,
                "usecase": "push_notifications_summarizer"
            }
        ))
```

### Run creation over stored completions (from `Create a Run` → `Using Stored Completions`)

```python
eval_run_result = await client.evals.runs.create(
    eval_id=eval_id,
    name="v1-run",
    data_source={
        "type": "completions",
        "source": {
            "type": "stored_completions",
            "metadata": {
                "prompt_version": "v1",
            }
        }
    }
)

print(f"Run ID: {eval_run_result.id}")
print(f"Status: {eval_run_result.status}")
print(f"Report URL: {eval_run_result.report_url}")
```

### Run creation with a different subject model (from `Using Completions with Different Models`)

```python
    tasks.append(client.evals.runs.create(
        eval_id=eval_id,
        name=f"gpt-5.6-terra-run-{prompt_version}",
        data_source={
            "type": "completions",
            "input_messages": {
                "type": "item_reference",
                "item_reference": "item.input",
            },
            "model": "gpt-6.1-sol",
            "source": {
                "type": "stored_completions",
                "metadata": {
                    "prompt_version": prompt_version,
                }
            }
        }
    ))
```

### Run results: the four counters and the per-criteria loop (from `Get Run Details`)

```python
run = client.evals.runs.retrieve(
    eval_id="eval_abc123",
    run_id="run_def456"
)

print(f"Run ID: {run.id}")
print(f"Status: {run.status}")
print(f"Started: {run.started_at}")
print(f"Completed: {run.completed_at}")

# Check results
if run.result_counts:
    print(f"\nOverall Results:")
    print(f"Total: {run.result_counts.total}")
    print(f"Passed: {run.result_counts.passed}")
    print(f"Failed: {run.result_counts.failed}")
    print(f"Error: {run.result_counts.errored}")

# Per-criteria results
if run.per_testing_criteria_results:
    for criteria_result in run.per_testing_criteria_results:
        print(f"\nCriteria {criteria_result.testing_criteria_index}:")
        print(f"  Passed: {criteria_result.result_counts.passed}")
        print(f"  Average Score: {criteria_result.average_score}")
```

### The page's own pass-rate idiom (from `List Runs`) — `errored` is not surfaced

```python
runs_response = client.evals.runs.list(
    eval_id="eval_abc123",
    limit=20,
    order="desc"
)

for run in runs_response.data:
    print(f"Run ID: {run.id}")
    print(f"Status: {run.status}")
    print(f"Name: {run.name}")
    if run.result_counts:
        print(f"Results: {run.result_counts.passed}/{run.result_counts.total} passed")
```

### Cursor pagination (from `List Evaluations`)

```python
evals_response = client.evals.list(
    limit=20,
    order="desc"
)

for eval in evals_response.data:
    print(f"Eval ID: {eval.id}, Name: {eval.name}")

# Check if there are more evals
if evals_response.has_more:
    # Fetch next page
    next_evals = client.evals.list(
        after=evals_response.last_id,
        limit=20
    )
```

### The only documented mutation surface for an eval (from `Update an Evaluation`)

```python
updated_eval = client.evals.update(
    eval_id="eval_abc123",
    name="Updated Evaluation Name",
    metadata={
        "version": "2.0",
        "updated_by": "user@example.com"
    }
)
```

### Run deletion (from `Delete a Run`)

```python
delete_response = await client.evals.runs.delete(
    eval_id="eval_abc123",
    run_id="run_def456"
)

print(f"Deleted: {delete_response.deleted}")  # True
print(f"Run ID: {delete_response.run_id}")
```

## Cross-References

**Candidates from `miner-related-notes.md`** (every listed path cited or
dismissed):

- `source-notes/docs-litellm-batches-api.md` — **cited** (Extends,
  Corroborates). That note is the corpus's precedent for *gateway metering
  that does not equal provider reality*: its Claim 6 records that batch TPM/RPM
  counters are "not reconciled against the provider's final usage" and that an
  unreadable input file is submitted unmetered, and its Claim 9 records
  Enterprise-gated batch cost tracking where "Batch cost tracking does not
  change the TPM or RPM counters reserved at submission." The evals page is
  the mirror image: it documents **no** metering at all for a workload that
  makes real model calls. Conversely, that note's Claim 3 (`batch_enqueued_token_limit`
  as an outstanding-work allowance) is what a *documented* budget knob for a
  batch-shaped workload looks like on this gateway — the evals surface has no
  equivalent, and no way to bound grader fan-out.
- `source-notes/docs-litellm-completion-web-search.md` — **dismissed**:
  provider-native search feature-boundary matrix; no eval corpus, grader, or
  result-count content.
- `source-notes/docs-litellm-enterprise.md` — **cited** (Extends). Its Claim
  3 inventories the gateway-wide governance features ("Enterprise adds SSO,
  audit logs, admin roles for each team, and help from the LiteLLM
  engineers.") and its Claim 4 the audit-log and per-team-logging story
  ("[Audit Logs with retention policies](/docs/proxy/audit_logs). Track every
  admin action and key-level change"). None of these is documented as applying
  to the `/evals` surface, so the page's per-eval credential comment
  (Claim 8 here) is the *only* tenancy mechanism documented for evals — and it
  is a code comment.
- `source-notes/docs-litellm-files-endpoints.md` — **dismissed**: `/files`
  passthrough and base64-encoded multi-account routing. The eval corpus is
  `stored_completions`, a different storage surface, and eval IDs are opaque
  (`eval_abc123`) with no documented routing payload.
- `source-notes/docs-litellm-generate-content.md` — **dismissed**: Google-native
  `generateContent` passthrough and its `safetySettings` governance; no eval
  content (shares only the corpus-wide "silently-delivered client config"
  family resemblance, not a claim-level bond).
- `source-notes/docs-litellm-bedrock-invoke.md` — **dismissed**: Bedrock native
  Invoke passthrough; no eval content.
- `source-notes/docs-litellm-a2a-iteration-budgets.md` — **cited**
  (Corroborates, Extends). Its Claim 4 ("Before each call, the accumulated
  spend is checked against the budget" / "After each successful LLM call, the
  response cost is accumulated for the session") is what a documented
  budget-semantics surface looks like on this gateway, and its Claim 5 ("When
  spend exceeds the budget, the request receives a **429 Too Many Requests**" /
  "Session budget exceeded for session session-abc-123. Current spend:
  $5.0032, max_budget_per_session: $5.00.") is the corpus's "one HTTP status,
  many meanings" warning. The evals surface adds a *third* case and in the
  opposite direction: its failure class — `result_counts.errored` — has no
  HTTP signal at all, living inside an otherwise successful payload
  (Claim 6 here).
- `source-notes/docs-litellm-audio-transcription.md` — **cited**
  (Corroborates, by contrast). Its Claim 5 records that the sibling non-chat
  endpoint page publishes a support matrix — Cost Tracking, Logging,
  End-user Tracking, Fallbacks, and Loadbalancing, with the lone Guardrails row
  qualified ("Applies to output transcribed text (non-streaming only)"). The
  `/evals` page publishes **no** such matrix, so the first two questions a
  platform team asks of a new LiteLLM surface — is it logged, is it metered —
  have no documented answer anywhere in the corpus for evals (Claim 8 here).
- `source-notes/docs-litellm-anthropic-advisor-tool.md` — **cited**
  (Extends). Its Claim 2 is the corpus's precedent for a *second* inference
  on the same gateway: "Advisor calls run as a separate sub-inference billed
  at the advisor model's rates" / "Top-level `usage` reflects executor tokens
  only." The evals grader is the same kind of second inference, but unlike the
  advisor there is no documented place where the grader's tokens or cost
  appear — no `usage` split, no spend record (Claim 4, Claim 8 here).
- `source-notes/docs-litellm-completion-input-params.md` — **dismissed**: its
  supported-params gate governs `/chat/completions` request bodies; the
  `/evals` endpoints are a different request surface, and the page's "extra
  body parameters" credential note is a management-API parameter outside that
  gate's scope. Its Claim 5 (prose default 600s vs code default `None`) is a
  page-local documentation defect, not a shared claim.

**Prospector-named overlaps:**

- `source-notes/docs-langfuse-evaluate-production-traffic.md` — **cited**
  (Corroborates, Extends). Its Claim 1 ("A rule defines **which** incoming
  observations are scored: filters, sampling rate, and one or more
  evaluators.") and Claim 2 ("Review the matching volume from the past seven
  days. For LLM-as-a-Judge, also review the estimated cost and lower the
  sampling rate if needed.") are the corpus's production-eval cost-control
  pattern. The LiteLLM surface has the retrieval half of that pattern
  (filter stored completions by metadata, Claim 2 here) with no sampling
  knob, no cost preview, and no always-on mode — a team that wants
  continuously-scored production traffic gets no such primitive here.
- `source-notes/docs-langfuse-evaluation-core-concepts.md` — **cited**
  (Corroborates). Its Claim 4 names the five-method taxonomy and its Claim 5
  defines the judge primitive ("LLM-as-a-Judge is an evaluation methodology
  where an LLM is used to assess the quality of outputs produced by another
  LLM application."). The `label_model` criterion (Claim 3 here) is that same
  primitive with a closed label set instead of a rubric score; the useful
  asymmetry is that Langfuse *names* the method and its blast radius
  ("Subjective assessments at scale") while the LiteLLM page does not name
  its grader type at all.
- `source-notes/docs-promptfoo-g-eval.md` — **cited** (Extends, by
  contrast). Its Claim 6 ("G-Eval makes one grader call to generate evaluation
  steps and another to score the output.") is the corpus's only documented
  grader *call count* — and therefore its only documented grader
  cost/latency multiplier. The evals page documents no call count, no
  concurrency, and no fan-out bound, so how many grader calls a run of N items
  makes is unstated (OQ-3).
- `source-notes/docs-promptfoo-evaluate-coding-agents.md` — **cited**
  (Extends, at the level of the gate contract). Its Claim 10 makes agent-eval
  regression gates concrete (cost/latency thresholds plus `--no-cache` and
  `--repeat 3`) and its Claim 13 sets the data-safety rule for eval harnesses
  (never production credentials or real customer data). The `/evals` surface
  provides no gate contract at all — no pass-rate threshold, no cost band, no
  repeat/no-cache knob, no run-level timeout — so "the eval is a gate" is
  entirely the caller's construction; and the corpus-safety rule has no
  counterpart, because the corpus *is* stored production-shaped content by
  construction (Claim 11 here).
- `source-notes/docs-litellm-mock-requests.md` — **cited** (Extends,
  precedent). Its Claim 9 ("The vendor's framing of `mock_response` is
  **cost, not coverage**") is the corpus's existing instance of the
  "what does this surface not attest to" extraction pattern; the evals page
  is the same pattern — a capability surface whose documentation never says
  what it bypasses (no guardrail, no logging, no budget, no rate limit is
  mentioned anywhere on it).
- `source-notes/docs-litellm-caching-hosted-cache.md` — **dismissed**:
  hosted response-cache lifecycle and the `caching=True` opt-in; the eval
  corpus is `stored_completions`, a different storage surface with no
  documented overlap.
- `source-notes/docs-litellm-cost-map-and-response-cost.md` — **cited**
  (Corroborates, Extends). Its Claim 1 ("LiteLLM returns `response_cost` in
  all calls." + accessor `response._hidden_params["response_cost"]`) is the
  corpus's one documented per-call cost handle. That accessor is a
  *completion-response* accessor: neither eval runs nor grader calls expose a
  cost field on this page, so the corpus's cost handle does not cover the
  evals surface.
- `source-notes/docs-litellm-gateway-auth-reference.md` — **cited**
  (Extends). Its Claim 7 ("Both surfaces use the `object_permission` model
  with intersection-style resolution, but at different depths today. MCP
  resolves across six levels; A2A across two.") establishes that LiteLLM's
  authorization model is per-surface and asymmetric. The `/evals` surface
  resolves nothing documented — a third depth in that family, and the reason
  the page's silence on list/delete authorization (Claim 8 here) is a real
  gap rather than a globally-answered question.

**Additional cross-references found by searching `source-notes/`:**

- `source-notes/docs-promptfoo-llm-as-a-judge.md` — **cited** (Corroborates).
  Its Claim 2 is the corpus's statement of the rule this page's schema
  half-implements: "Exclude these rows from agreement calculations and report
  their count alongside the number of judged rows." LiteLLM's `errored` bucket
  is the gateway-side instance of that discipline — a fourth counter that
  could carry grader failures — but the page never says what fills it, and
  its own quickstart divides by `total` and folds the distinction away
  (Claim 6 here). Its Claims 1 and 3 (calibration on a golden set and a
  never-tuned holdout, target agreement >90% before trusting the judge in CI)
  also have no counterpart on the `/evals` page: it pins no calibration
  workflow for the `label_model` grader.
- `source-notes/docs-promptfoo-configuration-outputs.md` — **cited**
  (Corroborates). Its Claim 3 is the corpus's clearest statement of the
  failure-classification discipline the `/evals` `errored` bucket is reaching
  for: "`failure` for failed assertions and `error` for provider/runtime errors
  so CI can distinguish incorrect behavior from execution problems".
  Promptfoo splits the two classes *in the CI artifact*; LiteLLM's schema has
  the fourth counter that could do the same, but never says what fills it and
  its own quickstart divides by `total` (Claim 6 here). Its Claim 1 (JUnit XML
  as the documented CI-gating format) and Claim 8 (`gradingResult` optional on
  a JSONL row, so a row can carry a missing verdict) are also the corpus's
  "what a CI-grade eval artifact must carry" reference point.
- `source-notes/blog-promptfoo-ai-regulation-2025.md` — **cited**
  (Corroborates, with a caveat). Its Claim 5 ("Evaluation artifacts:
  red-team results for tool misuse, prompt injection, and data leakage") is
  the source the guide turns into the compliance rule at
  `guide/06-security-and-trust.md:471` ("**Rule**: Your eval pipeline output
  IS your compliance evidence."). The `/evals` surface is
  consistent with that rule's *intent* (a `report_url` is a dated artifact)
  but undercuts its *mechanics*: run results are destructible on delete and
  `report_url` is the only artifact pointer, with no documented retention or
  export step (Claim 7, Claim 10 here). The corpus's other eval-tool notes
  (`docs-promptfoo-configuration-outputs.md`,
  `docs-promptfoo-enterprise-findings-reports.md`) are the places where
  exportable, dated artifacts are actually specified — the latter's Claim 8
  ("Reports are point-in-time scans of your target that are generated when you
  run a scan. These reports can be used to review the findings from a
  specific scan.") is the exact artifact discipline the LiteLLM surface
  leaves to the caller — and the LiteLLM page specifies no output or export
  format at all.

**Contradicts**: None. No existing source note makes a claim about evaluation
execution that this page opposes. Verified: a string search for
`stored_completions|testing_criteria|label_model|evals_api` across
`source-notes/` returns zero hits (no note covers this API surface), and the
Langfuse/Promptfoo notes describe different products with different surfaces.
The two candidate tensions flagged in triage were analyzed per MINER §4a and
resolved as non-contradictions: (a) the guide's "Multi-turn evals serialize,
and their failures do not localise" (`guide/05-llm-ops-reliability.md:610`,
sourced from `docs-promptfoo-chat-threads`) is a claim about a *different
product's* `_conversation` mechanism; the `/evals` page says nothing about
multi-turn, concurrency, or serialization, so it neither supports nor opposes
it — recorded as silence (OQ-3), not as a conflict; (b) the guide's
compliance rule (`guide/06-security-and-trust.md:471`) is a *requirement*, and
the `/evals` page is a *capability surface* that does not implement
  retention — a gap in the product, not an opposing claim. The 20
  `contradiction`-labeled issues and `CONTRADICTIONS.md` were checked; none
concerns evals or this page, so no duplicate exists. **No contradiction issue
filed.**

**Novel**: First source note in the corpus covering the LiteLLM gateway's
`/evals` surface. New to the corpus: the evals CRUD + runs CRUD endpoint
inventory; the `stored_completions` + request-`metadata` corpus contract at
two levels; the categorical `label_model` / `passing_labels` grader contract
and its `{{item.input}}` / `{{sample.output_text}}` templating; the
four-counter run result model including the separate `errored` bucket; the
`per_testing_criteria_results[].average_score` shape; cursor pagination via
`has_more` / `last_id`; the immutability of `testing_criteria` (update is
`name` + `metadata` only) and the absence of any `runs.update`; the
destructive delete-run semantics; the free-text run `name` field; and the
`input_messages` / `item_reference` model-comparison form. The corpus's
existing eval coverage — Langfuse's Rule-based online scoring and
five-method taxonomy, Promptfoo's judge calibration and CI gates — supplies
the *methodology*; the LiteLLM page supplies the *gateway-side plumbing* for
running an eval where LLM traffic already flows, plus the first corpus
evidence of a gateway-hosted **error-class bucket** (`errored`) that a
failure-classification rule can bind to.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**:
  (1) Extend the failure-classification discipline with the gateway-side
  instance of a **separate error bucket**: a run result exposes `total`,
  `passed`, `failed`, and `errored` as four counters, so a gate *can* keep
  harness failures out of quality failures — but the LiteLLM page defines
  none of them, and its own quickstart divides by `total`, which silently
  turns a grader outage into a quality regression (Claim 6). Recommend the
  chapter state the rule generically: *a gate must report the errored class
  separately and must not fold it into the denominator*, and name LiteLLM's
  `result_counts.errored` as the field that makes this expressible.
  (2) Add a "the eval contract is immutable" caveat to any
  prompt-regression-gating guidance built on this surface: `client.evals.update`
  changes only `name` and `metadata`, so a rubric or corpus-filter change
  requires a *new* eval object and fragments run history (Claim 10).
  (3) Add "the run label is not the model" to the model-migration guidance:
  `name` is free text and the vendor's own example labels runs
  `gpt-5.6-terra-run-*` while evaluating `gpt-6.1-sol`; and because runs
  cannot be updated, a wrong label can only be deleted (Claim 5, Claim 10).
  (4) Extend the canary/eval-gate section with the gateway-side eval corpus
  pattern: the corpus is stored completions filtered by request `metadata`,
  and the vendor's own workflow *generates* that corpus through the proxy —
  so "eval what you actually serve" requires tagging traffic at request time,
  and the guide's rule on clustering traffic to find eval-coverage gaps
  (`guide/02-observability.md:199`) has no automated counterpart on this
  surface (Claim 2, Claim 11).
  (5) Flag the unresolved subject-semantics ambiguity for the
  model-comparison workflow: the `input_messages` / `item_reference` form
  supports both "grade the stored output" and "re-run the stored input
  through `model`" readings, and the page gives a reader no way to choose
  (Claim 12).
- **Chapter 02 (Observability)**:
  (1) Add the four-counter run-result model to the metrics discussion and the
  rule that a pass rate computed as `passed/total` (the vendor's own idiom)
  is not a quality metric when a third of the population errored (Claim 6).
  (2) Note that the gateway's own Spend Tracking and Logging pages contain no
  mention of `/evals` or `stored_completions`, so nothing in the vendor
  documentation establishes that eval runs or grader calls are logged,
  metered, or attributed to a key — a team must verify this on its own
  deployment before treating the eval surface as observable (Claim 8).
  (3) Note the corpus-plumbing fact for the coverage section: the eval
  corpus is selected by request `metadata` at run time, with no sampling
  rate and no always-on mode, unlike the corpus's Rule-based online
  evaluation (Claim 2, Cross-References).
- **Chapter 06 (Security and Trust)**:
  (1) Extend the compliance-evidence rule at
  `guide/06-security-and-trust.md:471`: this surface produces a dated
  artifact (`report_url`) but the run results are destructible ("Permanently
  delete a run and its results.") and no export step, retention window, or
  report authentication is documented — so a team following the rule must
  export the report before deleting the run, and must confirm who can read
  the URL (Claim 7, Claim 10).
  (2) Add the grader-prompt egress fact: the grader prompt embeds the
  original user content and the subject model's output (`{{item.input}}`,
  `{{sample.output_text}}`) and is sent to the criterion's own model, which
  may be a different provider — a cross-provider data flow the docs do not
  mention (Claim 4).
  (3) Add the credential-storage question: the page's only tenancy statement
  is that model-specific credentials can be supplied "in the extra body
  parameters" for an evaluation, with no statement of where the credential
  lives, who it is scoped to, or whether it is persisted with the eval
  object (Claim 8, OQ-7).
  (4) Add the inventory hazard: `evals.list` takes no ownership filter and
  the list surface is documented as returning everything, so the eval
  catalogue of a shared proxy is enumerable by any caller with list access,
  and `last_id` is a cursor whose misreading can turn into a wrong-object
  update or delete on a permanent-delete surface (Claim 8, Claim 9).

## Extraction Notes

- Source read in full via WebFetch on the canonical URL
  (`https://docs.litellm.ai/docs/evals_api`, HTTP 200, no paywall, no
  truncation), then re-read as the page's own raw markdown
  (`https://docs.litellm.ai/docs/evals_api.md`, 458 lines, front matter
  `last_updated: "2026-10-20"`) so that every quoted code artifact is
  character-for-character what the vendor published. The page is a complete
  leaf: `What are Evals?`, `Quick Start` (proxy start + OpenAI/AsyncOpenAI
  client), `Evaluation Management` (create / list / retrieve / update /
  delete), and `Evaluation Runs` (create from stored completions, create with
  a different model, list, retrieve, delete).
- `related:` pages `/docs/proxy/managed_finetuning` and
  `/docs/generateContent` were fetched and checked (2026-10-22): each links
  *to* `/evals` in its own `related:`/navigation lists and contains no eval
  content of its own. Neither was extracted. Two adjacent gateway pages were
  consulted for gap-checking only and are cited in Claim 8:
  `/docs/proxy/cost_tracking` and `/docs/proxy/logging` (both raw markdown
  fetched 2026-10-22; neither contains `/evals` or `stored_completions`; the
  only eval-adjacent token in the Logging page is the `deepeval` callback).
- Triage bounding honored (#1691, `triaged:text`, `priority:low`). The
  Prospector's numbered items were extracted as follows: the CRUD params and
  paging fields (`limit`, `order`, `after`, `has_more`, `last_id`) → Claim 9;
  the criterion shape (`label_model`, `model`, `input`, `passing_labels`,
  `labels`) → Claim 3; `runs.create(eval_id, name, data_source)` with the
  nested `{"type": "completions", "source": {"type": "stored_completions",
  "metadata": {...}}}` shape and the returned `status` / `report_url` →
  Claims 2, 7, 12; `result_counts.total/passed/failed/errored` and
  `per_testing_criteria_results[].average_score` → Claim 6; the
  `{{item.input}}` / `{{sample.output_text}}` placeholders and the per-eval
  credential override → Claims 4, 8.
- **Open questions recorded (not answered by the page, not inferred)**:
  - OQ-1 — how a run's `data_source.source.metadata` filter composes with the
    eval's `data_source_config.metadata` filter (replace vs intersect).
  - OQ-2 — what populates `result_counts.errored`; whether errored items are
    inside `total`; whether `passed + failed + errored == total`; the scale
    of `average_score` for a categorical criterion.
  - OQ-3 — grader fan-out: how many grader calls a run of N items makes,
    the concurrency bound, and whether grader calls draw on the caller's
    rate limits, virtual-key budget, or spend.
  - OQ-4 — the full template-variable vocabulary behind `{{item.input}}` /
    `{{sample.output_text}}`, and whether `item.input` denotes the stored
    completion's input messages or its whole record.
  - OQ-5 — the `status` value set, which values are terminal, the polling
    contract, and whether a non-null `completed_at` is equivalent to a
    terminal status.
  - OQ-6 — what `report_url` points at: its contents, its lifetime, and
    whether it requires proxy authentication.
  - OQ-7 — where per-eval model credentials come from, who they are scoped
    to, and whether they are persisted with the eval object.
  - OQ-8 — allowed `order` values, the default order, and the maximum
    `limit`.
  - OQ-9 — how stored completions are written, how long they are retained,
    and whether they can be deleted.
- All `Quote` fields and Concrete Artifacts are verbatim contiguous
  fragments copied character-for-character from the raw markdown of the source
  page; no splicing of non-adjacent sentences inside a single quote. Where the
  reading is the Miner's synthesis rather than the page's words (the two-level
  filter composition, the "the quickstart is the trap" reading, the
  cursor-vs-id hazard, the shared-namespace content-egress risk, the
  immutability consequence), it is placed in `Our assessment` and labeled as
  inference.
- `confidence_overall` is `settled`, per the Prospector's explicit bounding
  instruction to capture documented surface behavior and parameter contracts
  as settled product behavior: every claim here is either a published
  endpoint/field/contract (deterministic, stated first-party) or an explicit
  *absence* verified section by section. The page contains no benchmark, no
  effectiveness claim, and no operational guidance, and none is inferred.
- `miner-related-notes.md` was read before writing Cross-References; all ten
  listed candidate paths are cited or dismissed above. Cross-reference
  verification (MINER §4b) re-read every cited claim in its own note —
  `docs-litellm-batches-api.md` (Claims 3, 6, 9), `docs-litellm-enterprise.md`
  (Claims 3, 4), `docs-litellm-a2a-iteration-budgets.md` (Claims 4, 5),
  `docs-litellm-audio-transcription.md` (Claim 5),
  `docs-litellm-anthropic-advisor-tool.md` (Claim 2),
  `docs-litellm-gateway-auth-reference.md` (Claim 7),
  `docs-litellm-cost-map-and-response-cost.md` (Claim 1),
  `docs-litellm-completion-input-params.md` (Claim 1),
  `docs-litellm-mock-requests.md` (Claim 9),
  `docs-langfuse-evaluate-production-traffic.md` (Claims 1, 2),
  `docs-langfuse-evaluation-core-concepts.md` (Claims 4, 5),
  `docs-promptfoo-g-eval.md` (Claim 6),
  `docs-promptfoo-evaluate-coding-agents.md` (Claims 10, 13),
  `docs-promptfoo-llm-as-a-judge.md` (Claims 1, 2, 3),
  `blog-promptfoo-ai-regulation-2025.md` (Claim 5) — no claim number is
  cited that does not resolve to a real numbered claim in the cited note, and
  every quoted fragment from a cited note was copied from that note.
- No contradiction issue filed; see the Contradicts section for the
  analysis of the two triage-flagged tensions and the verification of open
  `contradiction`-labeled issues plus `CONTRADICTIONS.md`.
- `date_published` is unknown (living Docusaurus page); `date_extracted` and
  `last_checked` are both 2026-10-22 (UTC).
