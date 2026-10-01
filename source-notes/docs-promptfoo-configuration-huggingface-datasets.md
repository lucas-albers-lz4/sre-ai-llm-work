---
source_url: https://www.promptfoo.dev/docs/configuration/huggingface-datasets
source_type: docs
title: "Promptfoo Configuration: Loading Test Cases from HuggingFace Datasets"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-30
date_extracted: 2026-10-01
last_checked: 2026-10-01
status: current
confidence_overall: emerging
issue: "#1526"
---

# Promptfoo Configuration: Loading Test Cases from HuggingFace Datasets

> The vendor reference for the `huggingface://datasets/<owner>/<repo>` prefix as
> a complete `tests:` source — and, more usefully for the guide, a documented
> third-party *data-plane* dependency for the eval gate. Primary contribution:
> the whole knob surface is three query parameters whose defaults are
> `split=test` / `config=default` / `limit=unlimited` with **no revision pin**,
> the rows arrive through HuggingFace's dataset-viewer `/rows` API at 100
> rows per request, variable expansion is switched off so array columns do not
> fan out into more test cases, and auth is presented as a rate-limit lever
> rather than a privacy one. That makes this page the remote-dataset twin of the
> guide's mutable-external-dataset hermeticity rule — and, unlike the
> synthesis path in `docs-promptfoo-dataset-generation.md`, the mutability is in
> a live third-party dataset the gate does not control.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "HuggingFace
  Datasets" configuration page under `/docs/configuration/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the loader's own query-parameter surface and
  defaults — authoritative for *what the config does*, directly checkable
  against an installed CLI plus a reachable `/rows` endpoint. Vendor-positioned:
  the page reports no measured latency, throughput, failure rate, or
  cost-per-eval figures for the loader, and offers no practitioner evidence
  about running it in CI. Page footer: "Last updated on **Sep 30, 2026** by
  **Michael**" (undated prose page, maintenance-bot/human last-edit stamp).
- **Scope**: The *importing* direction — pulling an existing HuggingFace dataset
  in as `tests:`. Covers the prefix syntax, the three query parameters and
  their defaults, the `/rows`-based loader mechanics, the three auth env vars,
  two worked configs, three example projects, and four troubleshooting
  entries. Does **not** cover the inverse direction (`promptfoo generate
  dataset`, which is `docs-promptfoo-dataset-generation.md` / #1277), the
  `huggingface:*` *provider* surface (HF models for inference — a different
  thing entirely, see `docs-promptfoo-classifier-grading.md`), red-team
  plugin configuration, or caching.
- **Sub-pages followed** (per MINER.md §1): the HuggingFace **dataset-viewer
  `/rows` API reference** (https://huggingface.co/docs/dataset-viewer/rows) —
  the endpoint promptfoo says it calls — and the promptfoo **Test Case
  Configuration** page (https://www.promptfoo.dev/docs/configuration/test-cases/),
  the page that *defines* the loader's row-to-test-case semantics and
  cross-links back to this one. Two claims (8, 9) depend on those sub-pages and
  are attributed as such.

## Extracted Claims

### Claim 1: `huggingface://datasets/<owner>/<repo>` is a complete `tests:` source, not a file path — every dataset row becomes one test case and every dataset field becomes a prompt variable, with no local `vars:` mapping and no per-row assertion block
- **Evidence**: The "Basic usage" section (`tests: huggingface://datasets/fka/awesome-chatgpt-prompts`
  replacing the whole `tests:` list), the "Use dataset fields in prompts"
  section (`{{question}}` bound straight to a dataset column with no
  declaration), and two "Implementation details" bullets that restate both
  halves.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Each dataset row becomes a test case with all dataset fields available as variables."
- **Our assessment**: The ergonomic appeal is also the hazard: a column *name*
  is the variable name, so the eval's prompt surface is determined by a
  third party's schema. Rename a column upstream and every `{{field}}` in the
  prompt silently binds to nothing — the vendor documents no schema-check
  failure mode (the only two "not found" troubleshooting entries cover the
  *dataset path* format and the *split*, neither is a field check). There is
  also no documented way to attach assertions to individual HF rows: the
  per-row `assert` / `description` / `metadata` surface of the Test Cases page
  has no HF equivalent on this page, so a mixed suite (HF rows **and** curated
  cases) can only be expressed by pairing `huggingface://` with sibling
  `- vars:` entries.

### Claim 2: The entire documented knob surface is `split` (default `test`), `config` (default `default`), `limit` (default `unlimited`) — and there is no revision, commit, or version pin at either the promptfoo layer or in the upstream API it calls
- **Evidence**: The three-row "Query parameters" table is the complete set, and
  a full read of the page surfaces no `revision=`, `ref=`, `sha`, `commit`, or
  "pin"/"version" option anywhere in the prefix syntax, the query string, the
  `env:`/auth sections, or the implementation notes. The upstream `/rows`
  endpoint parameterizes the same way (see Claim 8): "The `/rows` endpoint
  accepts five query parameters" — `dataset`, `config`, `split`, `offset`,
  `length` — with no revision slot either.
- **Confidence**: settled for the documented table; the "no revision pin
  exists" half is an absence-based finding and is graded as part of an
  otherwise-settled claim because it is corroborated by the upstream API's own
  parameter list (Claim 8) rather than resting on the promptfoo page alone.
- **Quote**: (query-parameter table, verbatim rows) "| `split` | Dataset split
  to load (train/test/validation) | `test` |" / "| `config` | Dataset
  configuration (also called a subset) | `default` |" / "| `limit` | Maximum
  number of test cases to load | `unlimited` |"
- **Our assessment**: This is the load-bearing hermeticity finding. The gate's
  test inputs are whatever `owner/repo` serves at fetch time, and there is no
  documented knob that changes that — which makes this a **stronger** instance
  of the guide's rule at `guide/05-llm-ops-reliability.md:213` than the
  synthesis path in `docs-promptfoo-dataset-generation.md` (Claim 5) is. There,
  the mutable reference is a *step you run* (regenerate with `-w` and you get a
  different fixture) and the documented mitigation is `emit with -o, commit,
  reference by file`. Here the mutable reference is a third party's live dataset
  that can change without anyone in the pipeline doing anything, and no
  committed-snapshot escape hatch is documented at all. A `revision=` the
  vendor does not expose is a *capability* gap, not a discipline gap: the
  guide's recommended remedy (materialize and commit the fixture) is the only
  available answer, and the page never mentions it.

### Claim 3: `limit` defaults to **unlimited** and the rows arrive 100 at a time over the HuggingFace dataset-viewer `/rows` API — so the default config fetches the entire dataset at eval time, and the only two remedies the page offers are `limit` and a token for higher rate limits
- **Evidence**: The `limit` row's default cell; the pagination sentence
  immediately under the table; the "Implementation details" bullet
  ("Large datasets are automatically paginated (100 rows per request)"); the
  "Performance issues" troubleshooting entry; and the Authentication callout
  that frames the token as a rate-limit lever for public data. Corroborated by
  the upstream endpoint: `length` is capped at `100` per request and the
  response carries a `num_rows_per_page` of `100` (Claim 8).
- **Confidence**: settled (documented product behavior, mechanically consistent
  with the upstream API's documented cap)
- **Quote**: "The loader uses the Hugging Face dataset viewer `/rows` API. Promptfoo manages `offset` and `length` for pagination; use `limit` to cap the total number of test cases."
- **Our assessment**: Read as an SRE cost/latency item, this is an eval-time
  *data-plane* fetch whose volume is a function of somebody else's dataset
  size, happening before a single provider call is billed. `tests:
  huggingface://datasets/rajpurkar/squad` with no query string means the gate
  materializes every row of SQuAD at CI time; pointed at a large public corpus
  it is a page-at-a-time crawl of an endpoint promptfoo does not control, from
  a runner whose egress and rate-limit budget are shared with the job that
  deploys the code. The page's own troubleshooting entry names the remedy as a
  performance fix ("Add the `limit` parameter to reduce the number of rows
  loaded"), which is the tell that the *default* is the wrong default for CI.
  Note also what is **not** documented: no timeout, no retry/backoff, and no
  behavior when the fetch fails partway (see Claim 9).

### Claim 4: Variable expansion is switched off for HF-loaded rows — array-valued dataset columns arrive intact instead of fanning out into multiple test cases, and the one documented global switch runs in the *opposite* direction, so the same logical dataset yields different case counts depending on which loader fetched it
- **Evidence**: The "Implementation details" bullet list; reconciled against the
  promptfoo Test Cases page, which defines what the switch means ("By default,
  array variables expand into multiple test cases. To pass an array directly to
  assertions like `contains-any`, disable variable expansion:") and against
  the Configuration Reference row `docs-promptfoo-configuration-guide.md` cites
  as "If true, arrays in vars are not expanded into multiple test cases". The
  page documents **no** inverse — no `expandVarExpansion`, no per-loader opt-in.
- **Confidence**: settled for the promptfoo bullet; emerging for the
  cross-loader divergence, which is the Miner's reconciliation of two
  documented behaviors and is not stated as such on either page.
- **Quote**: "Variable expansion is disabled to preserve original data"
- **Our assessment**: The word "expansion" is doing quiet work here. On this
  page it means *array → cartesian product of test cases*, not `{{field}}`
  prompt templating — which the same page clearly keeps enabled (the "Use
  dataset fields in prompts" section). So the mechanical effect is: a list-valued
  HF column yields **one** test case holding an array, not N cases. Two
  consequences for the guide. (a) It flips the cost/coverage trade documented at
  `docs-promptfoo-configuration-guide.md` Claim 12: array expansion is the
  documented way a suite quietly multiplies into an expensive, timeout-prone
  matrix, and the HF loader silently *removes* that multiplication — the same
  rows in a `file://tests.json` fixture and behind
  `huggingface://datasets/...` are not the same suite, so a coverage or cost
  comparison across the two loaders is not like-for-like. (b) It is
  unconditional, so `defaultTest.options.disableVarExpansion: true` is redundant
  here and there is no documented way to get expansion *back*. For an SRE
  reading the rule this yields is narrow and useful: **a HF-loaded gate's case
  count is a function of the remote schema's column types, which the pipeline
  does not own.** The stated reason ("to preserve original data") is coherent —
  it is the same state the Test Cases page uses deliberately when passing an
  array straight into `contains-any` — so this is a disclosed default, not a
  doc bug. It is recorded here because the disclosure sits on a different page
  from the promise.

### Claim 5: `split` defaults to `test` and the documented symptom of getting it wrong is **empty results**, not an error — a wrong split or config yields a zero-case eval, which is a CI gate that passes without testing anything
- **Evidence**: The `split` and `config` default cells (`test`, `default`); the
  "Empty results" troubleshooting entry, which names the default-split case
  explicitly; the MMLU example, which exists precisely because `config` must be
  set for multi-subset corpora; and the absence of any "unknown split" error in
  the troubleshooting set (which instead covers auth, dataset-not-found, empty
  results, and performance).
- **Confidence**: settled (documented product behavior; the "yields zero cases"
  consequence is the Miner's reading of a documented `returns no results`
  symptom, graded `emerging` in that half only)
- **Quote**: "Check that the specified split exists for the dataset. Try `split=train` if `split=test` returns no results."
- **Our assessment**: This is a seventh entry for the guide's "A gate that
  cannot fail is not a gate" table at `guide/05-llm-ops-reliability.md:655` —
  and the most dangerous one there, because unlike `threshold: 0` or
  `weight: 0` it is **not visible in the config at all**. Every existing row in
  that table is a config line a reviewer can spot in a diff. This one lives on
  the *other* side of a network call: the config reads `tests:
  huggingface://datasets/<owner>/<repo>`, looks complete, and yields a run with
  no cases in it. Add the sibling failure from the same table: `config`
  defaulting to `default` means an MMLU-shaped dataset (many named subsets)
  with a valid `split=test` but no `config=` still resolves to nothing — the
  page's own MMLU example is the workaround it offers ("To load a specific
  subset (common with MMLU datasets), set `config`:"). The actionable
  recommendation for Ch05 is therefore a pipeline invariant, not a config
  lint: **a CI eval gate must assert a non-zero (and ideally an
  expected-minimum) test-case count before interpreting its verdict**, because
  for this loader the zero-count path is a documented, non-error outcome.

### Claim 6: Auth is three interchangeable environment variables, and the page positions the token as a **rate-limit** dependency rather than only a privacy one — a CI gate's throughput is bound to a credential even for fully public data
- **Evidence**: The Authentication section's shell block exporting all three
  names, and the info callout underneath it that distinguishes private/gated
  from public-then-rate-limits.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Authentication is required for private datasets and gated models. For public datasets, authentication is optional but provides higher rate limits."
- **Our assessment**: Two operational consequences worth writing down. First,
  the credential is not an edge case for private data — it is a *throughput*
  dependency on the public path too, which interacts directly with Claim 3's
  `limit: unlimited`: the unbounded default is the configuration most likely to
  be rate-limited, and the documented mitigation is to add a secret to the
  runner. So the safe CI shape of this config is a least-privilege, read-only
  HF token in the runner environment (a rate-limit purpose needs nothing
  broader), and a runner that has it is a runner whose credential inventory now
  includes one more vendor token. Second, a naming trap specific to this page:
  the datasets loader accepts `HF_TOKEN`, `HF_API_TOKEN`, **and**
  `HUGGING_FACE_HUB_TOKEN`. The sibling `classifier`-assert path documents only
  the first two (`docs-promptfoo-classifier-grading.md` Claim 8), so a team
  that standardized on HuggingFace's own canonical `HUGGING_FACE_HUB_TOKEN`
  name will find the classifier path undocumented against it. Not a
  contradiction (the datasets list is a strict superset), but a real
  credential-surface mismatch to record in Ch06.

### Claim 7: The vendor's own worked config puts the HuggingFace token in `config.env` — the exact pattern a sibling promptfoo page warns may resolve the secret into the eval config object and surface it in exported results
- **Evidence**: The "Question answering with limits" example, whose full config
  includes an `env:` block holding the token as a literal; set against
  `docs-promptfoo-configuration-guide.md` Claim 7, which records the vendor's own
  warning that a secret placed in `config.env` "resolves the secret into the
  eval config object and may appear in exported results".
- **Confidence**: settled for both halves — the YAML is on this page, the
  warning is quoted from the cited sibling note (verified per MINER.md §4b).
- **Quote** (this page, verbatim YAML): "env:\n  HF_TOKEN: your_token_here"
- **Our assessment**: The HF datasets page's *only* authenticated example
  demonstrates the credential-handling pattern that the configuration-guide
  page explicitly cautions against, and it does so without a warning of its
  own. `config.env` also means the token is evaluated as config, not process
  environment: the same sibling note records that `{{ env.X }}` is resolved at
  **config load time, not runtime**, so an env-block credential is part of the
  evaluated config object rather than the runner's process state. An operator
  copying this example verbatim gets a short-lived-looking token in a file that
  a share/export path may pick up. The guide-level rule is small and concrete:
  **prefer process-env credentials (`export HF_TOKEN=...`, which this same page's
  Authentication section documents) over `config.env` for the HF loader**, and
  audit what the eval exports. This is a good example for Ch06's credential
  section precisely because the vendor's own reference demonstrates the
  anti-pattern.

### Claim 8: The upstream dataset-viewer adds dependencies and degradations the promptfoo page never mentions — the dataset must be parquet-backed, an oversized dataset comes back `partial`, and media columns resolve to **expiring signed URLs** over a viewer asset cache that gets emptied
- **Evidence**: The HuggingFace `/rows` reference (sub-page, not the promptfoo
  page): the parquet-export restriction, the `length` cap of `100`, the
  `partial` flag's meaning, the image/audio `src` field's signed-URL expiry, and
  the asset-caching paragraph.
- **Confidence**: settled as HuggingFace-documented endpoint behavior; the
  operational consequence for promptfoo gates is the Miner's inference, since
  the promptfoo page documents none of it.
- **Quote** (dataset-viewer `/rows` reference, verbatim): "`length`: the length
  of the slice, for example `10` (maximum: `100`)" and "If the result has
  `partial: true` it means that the slices couldn't be run on the full dataset
  because it's too big." and "The images and audio samples are cached by the
  dataset viewer temporarily. Internally we empty the cached assets of certain datasets from time to time based on usage."
- **Our assessment**: Three gaps between what an operator assumes and what the
  endpoint does, none of which the promptfoo page surfaces. (1) **Parquet-only**:
  a dataset without a parquet export is not loadable through this path at all,
  and the symptom an operator will meet is not obviously a promptfoo problem.
  (2) `partial: true` is a *silently shortened* result — the endpoint
  acknowledges it could not slice the full dataset and hands back a partial
  answer, which from the CI log looks identical to a smaller dataset. A gate
  that thinks it ran N cases may have run fewer. (3) **Multimodal rot**: image
  and audio cells come back as signed URLs with a stated expiry, backed by a
  viewer cache that is periodically emptied. For an HF-dataset *vision* eval
  that is the sharpest form of the non-hermeticity in Claim 2 — the input
  bytes are not in the repo, are not guaranteed to still resolve on the second
  run, and the documented recovery is to re-call `/rows`. The 100-row cap is the
  mechanical reason promptfoo's page count (Claim 3) is what it is: the
  endpoint's own ceiling, not a promptfoo tuning choice.

### Claim 9: Hermeticity is restored only *after* the first fetch, and only for a saved run — promptfoo persists parsed test rows with the evaluation so resume/retry reuse them "including generated and remote datasets", and nothing on this page documents retry, backoff, or timeout for the fetch that gets them
- **Evidence**: The Test Case Configuration page's Path Resolution section
  (sub-page, not this page) states the persistence and reuse behavior
  explicitly and names remote datasets; and this page documents no
  fetch-failure policy at all — the four troubleshooting entries are split
  (`test` does not exist), dataset-not-found (path format), empty results, and
  "performance" (add `limit`). Contrast `docs-promptfoo-configuration-caching.md`
  Claim 7, where 429/backoff *is* documented for provider calls.
- **Confidence**: emerging (the persistence behavior is settled and documented;
  "no fetch-level retry is documented" is an absence-based finding, and the
  asymmetry with the provider path is the Miner's reading across two notes)
- **Quote** (Test Case Configuration page, verbatim): "CLI evaluations save
  parsed test rows, external defaults, and an absolute base directory. Resume and
  retry reuse those rows, including generated and remote datasets. Run a new
  evaluation to pick up changed test sources."
- **Our assessment**: This is the partial answer to Claim 2, and it changes the
  rule rather than repeating it. A promptfoo evaluation is *not* a live view of
  the dataset: the rows are snapshotted into the saved run, so resume/retry of
  **that run** is hermetic with respect to the remote dataset. The gap is that
  the hermeticity begins at first fetch — every new `promptfoo eval` re-reads
  `owner/repo`, and the same doc sentence makes the operational requirement
  explicit: "Run a new evaluation to pick up changed test sources," which is to
  say a canary run and its control run are not guaranteed to share inputs unless
  the *saved run* is what you compare. For a canary-vs-control gate that is the
  concrete rule: compare within a saved evaluation, or the mutable reference
  (Claim 2) sits between your arms. On the failure side, the documented retry
  posture covers *provider* calls (429 with exponential backoff, 5xx gated on
  `PROMPTFOO_RETRY_5XX` — `docs-promptfoo-configuration-caching.md` Claim 7);
  this page offers no equivalent for the dataset fetch, so a rate-limited
  `/rows` crawl is an undocumented failure mode on the path Claim 3 makes
  unbounded by default. Stated as absence, deliberately: the loader may well
  retry internally, but the docs do not say so, and a CI gate's input
  acquisition should not be the one hop on the critical path without a
  documented failure policy.

## Concrete Artifacts

### Query-parameter surface (verbatim from the "Query parameters" table)

| Parameter | Description | Default |
|---|---|---|
| `split` | Dataset split to load (train/test/validation) | `test` |
| `config` | Dataset configuration (also called a subset) | `default` |
| `limit` | Maximum number of test cases to load | `unlimited` |

### Implementation details (verbatim bullet list)

```
- Each dataset row becomes a test case
- All dataset fields are available as prompt variables
- Large datasets are automatically paginated (100 rows per request)
- Variable expansion is disabled to preserve original data
```

### Authentication (verbatim from the "Authentication" section)

```bash
# Any of these environment variables will work:
export HF_TOKEN=your_token_here
export HF_API_TOKEN=your_token_here
export HUGGING_FACE_HUB_TOKEN=your_token_here
```

### Worked configs (verbatim from "Example configurations")

Basic chatbot evaluation:

```yaml
description: Testing with HuggingFace dataset

prompts:
  - 'Act as {{act}}. {{prompt}}'

providers:
  - openai:gpt-5-mini

tests: huggingface://datasets/fka/awesome-chatgpt-prompts?split=train
```

Question answering with limits — **note the `env:` credential block (Claim 7)**:

```yaml
description: SQUAD evaluation with authentication

prompts:
  - 'Question: {{question}}\nContext: {{context}}\nAnswer:'

providers:
  - openai:gpt-5-mini

tests: huggingface://datasets/rajpurkar/squad?split=validation&limit=100

env:
  HF_TOKEN: your_token_here
```

Split / config / limit forms (verbatim from "Dataset splits" and "Query parameters"):

```yaml
# Load from training split
tests: huggingface://datasets/fka/awesome-chatgpt-prompts?split=train

# Load from validation split with custom configuration
tests: huggingface://datasets/fka/awesome-chatgpt-prompts?split=validation&config=custom

# Cap the total number of test cases
tests: huggingface://datasets/fka/awesome-chatgpt-prompts?split=train&limit=50

# Multi-subset corpus — `config` is required here
tests: huggingface://datasets/cais/mmlu?split=test&config=college_physics&limit=10
```

Dataset fields bound directly as prompt variables (verbatim from "Use dataset
fields in prompts"):

```yaml
prompts:
  - "Question: {{question}}\nAnswer:"

tests: huggingface://datasets/rajpurkar/squad
```

### Troubleshooting table (verbatim entries — the four documented failure modes)

| Symptom | Documented fix |
|---|---|
| Authentication errors | Ensure your HuggingFace token is set correctly: `export HF_TOKEN=your_token` |
| Dataset not found | Verify the dataset path format: `owner/repo` (e.g., `rajpurkar/squad`) |
| Empty results | Check that the specified split exists for the dataset. Try `split=train` if `split=test` returns no results. |
| Performance issues | Add the `limit` parameter to reduce the number of rows loaded: `&limit=100` |

### Example projects (verbatim table — note the third row's red-team use)

| Example | Use Case | Key Features |
|---|---|---|
| Basic Setup — `examples/huggingface/dataset` | Simple evaluation | Default parameters |
| MMLU-Pro Comparison — `examples/compare-gpt-model-tiers-mmlu-pro` | Query parameters | Split, config, limit |
| Red Team Safety — `examples/redteam-beavertails` | Safety testing | BeaverTails dataset |

All paths above are under `https://github.com/promptfoo/promptfoo/tree/main/`.
The `huggingface/dataset` example README was fetched and confirms it is a
boilerplate init example ("You can run this example with: `npx promptfoo@latest
init --example huggingface/dataset`") carrying no extra loader configuration —
the docs page is the whole documented surface.

### Upstream endpoint contract (verbatim from the HuggingFace dataset-viewer `/rows` reference)

```
The `/rows` endpoint accepts five query parameters:

- `dataset`: the dataset name, for example `nyu-mll/glue` or `mozilla-foundation/common_voice_10_0`
- `config`: the subset name, for example `cola`
- `split`: the split name, for example `train`
- `offset`: the offset of the slice, for example `150`
- `length`: the length of the slice, for example `10` (maximum: `100`)
```

Request shape, verbatim from the same page's `curl` sample:

```bash
curl https://datasets-server.huggingface.co/rows?dataset=ibm/duorc&config=SelfRC&split=train&offset=150&length=10 \
        -X GET \
        -H "Authorization: Bearer ${API_TOKEN}"
```

Response envelope, verbatim tail of the page's `ibm/duorc` example — note
`num_rows_total`, the `100` page size, and the `partial` flag:

```json
  "num_rows_total":60721,
  "num_rows_per_page":100,
  "partial":false
}
```

Source for this last block: https://huggingface.co/docs/dataset-viewer/rows
(the endpoint behind Claim 8). All other artifacts:
https://www.promptfoo.dev/docs/configuration/huggingface-datasets — sections as
noted. Code blocks copied character-for-character from the rendered pages,
except that line breaks lost in HTML extraction were restored at
YAML/shell/comment boundaries with no wording changes (the sibling #1289/#1513
notes use the same convention). For spot-checks: the authenticated SQUAD config
above carries the page's own `split=validation`, and the MMLU line carries the
page's own `config=college_physics` (Claim 5).

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-dataset-generation.md` **Claim 5**
    ("generated test cases are non-deterministic by construction and the
    documented surface offers no pinning, versioning, or seed story") — the
    guide's counter-example at `guide/05-llm-ops-reliability.md:216` names the
    generator as the mutable external dataset. This page supplies the **second,
    harder** instance: same rule, but the mutable reference is a live
    third-party dataset rather than a step in your own pipeline, and no
    documented `revision=` knob exists to pin even in principle (Claim 2).
    The two notes together bound the guide's paragraph — a prompt config that
    references a mutable external dataset is non-hermetic, and promptfoo offers
    two documented ways to get there. (Verified: #1277 Claim 5.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 2**
    ("deterministic in promptfoo's sense means *no model judge*, not *no
    external dependency*") — the vendor-draws-the-line finding at the
    *assertion* tier. This page is the same discipline at the *test-source*
    tier: `limit: unlimited` + `/rows` pagination + `env:` credentials is a
    deterministic assertion suite whose inputs arrive over the network. Read
    together they support one guide sentence — no judge in the loop does not
    mean hermetic. (Verified: #1289 Claim 2.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 4**
    (cached entries replay "for up to two weeks after a provider silently
    changes model behavior") — the cache-side route to "green gate, no
    evidence"; this page is the input-side route, and Claim 9's saved-test-rows
    behavior is the *same* snapshot-durability property applied to test data.
    Two different caches (response cache, saved evaluation) with the same
    consequence: the artifact you are looking at may describe a past state of a
    mutable input. (Verified: #1275 Claim 4.)
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 12**
    ("array-valued vars expand to the cartesian product of their values, and
    the escape hatch (`disableVarExpansion`) lives on `defaultTest.options`") —
    this page documents the loader forcing the *non-default* state
    unconditionally (Claim 4). The sibling note establishes what the default
    is and why it is expensive; this note establishes that a HF-loaded suite
    silently opts out of it. The two are only legible together, which is why
    the cross-loader case-count divergence is recorded as Claim 4. (Verified:
    #1513 Claim 12, including its verbatim quotation of the Test Cases page's
    "By default, array variables expand into multiple test cases" and the
    Configuration Reference row "If true, arrays in vars are not expanded into
    multiple test cases".)

- **Contradicts**: None identified; no contradiction issue filed. Checked
  `CONTRADICTIONS.md` (no `C-NNN` entries beyond the unrelated LiteLLM-routing
  case) and all ten open `contradiction`-labeled issues (#1517, #1514, #1486,
  #1462, #1461, #1408, #1352, #1338, #1322, #1307) — the closest, #1307, is
  about promptfoo trace-assertion throw-vs-green semantics and shares no claim
  with this page. The two candidates I considered and rejected as MINER.md
  §4a "not when to file": (a) the page's "Variable expansion is disabled to
  preserve original data" against the Test Cases page's "By default, array
  variables expand into multiple test cases" — a **per-loader override**, i.e.
  a conditioning variable, and it is disclosed on the loader's own page;
  (b) the extra `HUGGING_FACE_HUB_TOKEN` env-var name against
  `docs-promptfoo-classifier-grading.md` Claim 8's two-name list — the datasets
  list is a strict **superset** naming three of which two match, so nothing
  opposes anything. Both are recorded in Claims 4 and 6 instead.

- **Extends**:
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 8** and
    **Claim 10** — the closest HuggingFace surface in the corpus, and the
    triage's warning not to conflate the two is respected: that note is the
    `huggingface:text-classification:` **provider** path, this page is the
    `huggingface://datasets/` **test-source** path. What this note adds is the
    third env-var name and the rate-limit framing (Claim 6), and a second
    instance of its Claim 10 thesis — "a `classifier` gate is a dependency on
    a remotely-hosted, mutable model endpoint" — on the input side: a
    HF-sourced gate depends on a remotely-hosted, mutable *dataset*. The
    guide's Ch06 dependency-with-a-lifecycle rule
    (`guide/06-security-and-trust.md:423`) currently covers the detector; it
    now needs a row for the dataset. (Verified: #1288 Claims 8 and 10.)
  - `source-notes/docs-promptfoo-configuration-guide.md` **Claim 7**
    (`{{ env.X }}` resolves at config load time and the vendor warns that
    secrets in `config.env` "may appear in exported results") — this page's
    worked authenticated config demonstrates that anti-pattern in the wild
    (Claim 7), which is stronger evidence than the warning alone: the
    credential-handling guidance is not being followed on the vendor's own
    example. Also **Claim 11** (multiple configs combine into a single eval,
    not reported separately) becomes load-bearing here — pairing a
    `huggingface://` source with curated cases, or with a second config, is one
    merged run, so a wrong split silently merges into an otherwise-healthy
    suite rather than failing the job. (Verified: #1513 Claims 7 and 11.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 7**
    (429 retried automatically with exponential backoff; 5xx only under
    `PROMPTFOO_RETRY_5XX`) — the documented retry posture for the *provider*
    leg of an eval run. Read against Claim 9, it locates the undocumented
    surface: the *dataset-fetch* leg has no documented retry, timeout, or
    partial-failure behavior on this page, which matters precisely because
    Claim 3's default makes that leg unbounded. (Verified: #1275 Claim 7.)
  - `source-notes/docs-promptfoo-dataset-generation.md` — the *inverse*
    direction of the same config field, and the sibling note's own Extraction
    Notes recorded "HuggingFace Datasets" as a followed-or-not next page. This
    note closes that gap: synthesis (`promptfoo generate dataset`) writes
    fixtures you can commit; remote import (`huggingface://datasets/`) reads
    fixtures you cannot. The guide should state both halves of the same rule
    rather than the synthesis half alone. (Verified: the gap is stated in
    #1277's Extraction Notes; no claim number fabricated for it.)

- **Novel**: First corpus coverage of the **`huggingface://datasets/` test-source
  loader** — grep across `source-notes/` finds zero prior hits for the prefix
  (the 33 existing "HuggingFace"/`HF_TOKEN` hits are all the `huggingface:*`
  *provider* or *classifier* surface, or LiteLLM unrelated). Specifically new:
  1. **A remote-dataset gate input with no revision pin** (Claim 2) — the
     strongest instance yet of the guide's hermeticity rule, because the
     mutable reference is third-party and unpinnable, not merely unversioned.
  2. **`limit: unlimited` + 100-row pagination as the CI default** (Claim 3) —
     an unbounded, rate-limit-exposed data fetch on the eval critical path.
  3. **Variable expansion forced off for this loader** (Claim 4) — the same
     dataset yields a different number of test cases via `file://` vs
     `huggingface://`.
  4. **The fail-open empty-suite path** (Claim 5) — `split=test` default with
     "returns no results" as the documented symptom; a gate that cannot fail
     whose cause is invisible in the config.
  5. **A rate-limit-scoped HF token as a CI credential** (Claim 6) plus the
     `config.env` anti-pattern in the vendor's own example (Claim 7).
  6. **Upstream viewer degradation modes the promptfoo page omits** — parquet
     requirement, `partial: true`, and expiring signed URLs for media cells
     (Claim 8).
  7. **Saved-test-rows as a partial hermeticity answer** (Claim 9) — inputs are
     snapshotted per evaluation, but only after the first fetch.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — hermeticity rule
  (`guide/05-llm-ops-reliability.md:197-214`, and specifically the
  "A generated dataset is the mutable external reference" section at
  :216-253)**: Extend the mutable-external-dataset counter-example from the
  *synthesis* path to the *remote-import* path. Today the paragraph teaches
  `emit with -o → commit → reference by file` and marks `-w` as the
  anti-pattern; that remedy is fully available to the reader because promptfoo
  synthesizes into a file. Add the harder case immediately after: a config
  reading `tests: huggingface://datasets/<owner>/<repo>` has the **same three
  query parameters and no revision pin at all** (Claim 2), fetches rows at
  eval time over `datasets-server.huggingface.co` in 100-row pages
  (`limit` defaults to `unlimited`, Claim 3), and therefore is not merely
  non-replayable but **not even pinnable in place**. The stated recommendation
  should be the same discipline with a harder constraint: materialize the HF
  rows into a committed fixture (`file://tests.json` / `.csv`) and point the
  gate at that, because the vendor exposes no pin to fall back on. Add the
  canary-shaped corollary from Claim 9: saved evaluations snapshot parsed test
  rows, so compare arms *within one saved run* — "Run a new evaluation to pick
  up changed test sources" means a second `promptfoo eval` re-reads the remote
  dataset. And extend the non-hermeticity catalog to *inputs*, not just config
  and assertions: a gate whose prompts are assembled from an HF row at fetch
  time is a config-run that embeds a live lookup, which the existing
  "Evaluation must stay separate from side effects" rule
  (`guide/05-llm-ops-reliability.md:254-264`) currently forbids in principle.
- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655-690`)**: This source contributes the
  first row for that table whose cause is **not in the config**. Every existing
  row (`threshold: 0`, `weight: 0`, bare `llm-rubric`, bare
  `context-faithfulness`/`recall`, `guardrails` with no normalized signal,
  custom-JS trace guard) is greppable in a diff; `split=test` +
  `config=default` defaults are not. Add the row — *HF-sourced `tests:` with a
  wrong or absent `split`/`config` runs zero cases and passes* (Claim 5) —
  and pair it with the pipeline invariant that closes it: **a CI eval gate must
  assert an expected-minimum test-case count before reading its verdict.** The
  same section's "read the assert's own defaults" checklist at
  `guide/05-llm-ops-reliability.md:443` should gain a **test-source** sibling:
  the loader's defaults (`split=test`, `config=default`, `limit=unlimited`) and
  its variable-expansion override are properties of a line a reviewer cannot
  see the far side of (Claims 2-5).
- **Chapter 05 — eval cost / latency accounting**: Add the data plane to the
  cost model. `limit: unlimited` means an eval's *input acquisition* cost and
  wall-clock are a function of somebody else's dataset size, incurred before any
  provider billing (Claim 3); and array-valued HF columns do **not** fan out, so
  a suite's case count — and therefore its provider spend — is set by remote
  column types the pipeline does not own (Claim 4). Recommend the guide state
  `split` + `config` + `limit` explicitly in every HF-backed gate config rather
  than inheriting three defaults, and record the resolved case count as eval
  provenance alongside the provider and model IDs.
- **Chapter 06 (Security and Trust) — "A classifier gate's detector is a
  dependency with a lifecycle" (`guide/06-security-and-trust.md:423-436`)**: The
  rule there pins model id + label set + threshold and re-verifies hosting and
  maintenance state. Add the **input-side** member of that family: an HF-sourced
  gate has a dataset dependency with the same lifecycle problem and none of the
  same controls — no revision pin (Claim 2), a column-rename that silently
  unbinds every `{{field}}` in the prompt (Claim 1), and upstream conditions
  the promptfoo page does not surface (parquet-only, `partial: true`,
  expiring signed URLs for media cells — Claim 8). The Ch06 recommendation
  should read: **the gate's dataset is a dependency to pin and re-verify on the
  same cadence as its detector, and because promptfoo cannot pin one, the pin
  must happen at the fixture layer.**
- **Chapter 06 — "Gateway credential routing: declare, don't infer"
  (`guide/06-security-and-trust.md:603`)**: Two additions. (a) The HF loader's
  token is a *throughput* dependency on the public path, not only a
  privacy dependency (Claim 6) — so it belongs in the credential inventory with
  its purpose stated (rate limits) and the narrowest scope that satisfies it,
  and its name reconciled against the `classifier` path's two-name surface.
  (b) The vendor's own authenticated example places the token in `config.env`
  (Claim 7), which the configuration-guide page warns may surface in exported
  results; the guide should carry the positive form — `export HF_TOKEN=...`
  (documented on this page) — and the audit rule (check what the eval exports),
  not the config-file form.
- **Chapter 06 — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`)**: The same prefix is the documented
  route for red-team dataset sourcing (the page's own example projects include a
  "Red Team Safety / BeaverTails dataset" entry, and its See Also section links
  Red Team Configuration "Using datasets in red team evaluations"). Worth one
  line: red-team corpora sourced this way inherit every trap above, and the
  existing no-jailbreak-baseline discipline at
  `guide/06-security-and-trust.md:364` is only meaningful if the baseline and
  the attack run read the *same* rows — which a re-fetch between them can
  silently prevent.

## Extraction Notes

- Source read in full via direct fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/huggingface-datasets), including
  the nav, the four troubleshooting entries, the example-projects table, and the
  See Also list. Two sub-pages followed per MINER.md §1 (max 5):
  the HuggingFace **dataset-viewer `/rows` API reference** (the endpoint the page
  says it calls — Claim 8) and the promptfoo **Test Case Configuration** page
  (which defines the row→test-case semantics, the `disableVarExpansion`
  semantics, and the saved-test-rows behavior — Claims 4 and 9). The
  `huggingface/dataset` example README was also fetched to check whether the
  docs' "Example projects" table hides configuration the page omits; it does
  not (boilerplate `init --example` README only). Pages **not** followed and
  why: `HuggingFace Provider` (`/docs/providers/huggingface/`) is the inference
  *provider* surface the triage explicitly warned against conflating; `Red Team
  Configuration` is a large separate page already covered elsewhere in the
  corpus; the prev/next siblings (`/docs/configuration/datasets/` = #1277, and
  `Scenarios`) are other extraction units.
- Every quote was copied character-for-character from the fetched rendered
  content, and each is attributed in-line to the page it came from — the
  promptfoo page, the HuggingFace `/rows` reference, or the Test Case
  Configuration page. Where a claim rests on the absence of a documented
  feature (no revision pin, no documented fetch retry, the three-name env-var
  superset), that is stated in the Evidence/Confidence/Our assessment fields
  rather than dressed up as a positive citation, per MINER.md §2a.
- **Contradiction handling**: no contradiction issue filed, per the reasoning in
  Cross-References → Contradicts — both candidates examined are a per-loader
  conditioning variable and a strict-superset naming difference, which MINER.md
  §4a lists as *not* grounds for filing. Verified against `CONTRADICTIONS.md`
  and all ten open `contradiction`-labeled issues.
- **Cross-reference verification (MINER.md §4b)**: every `Claim N` cited above
  was re-read in the cited note before writing — #1277 Claim 5,
  #1288 Claims 8 and 10, #1289 Claim 2, #1275 Claims 4 and 7, #1513 Claims 7,
  11 and 12 (including the two verbatim strings this note reuses from #1513's
  own quotation of the Test Cases and Configuration Reference pages). The
  #1277 gap reference is to that note's Extraction Notes by section name, not
  to a claim number. Claims 1-9 are this note's own numbering.
- `confidence_overall` is `emerging`, consistent with the sibling promptfoo
  config notes (#1275, #1277, #1289, #1288, #1513): the parameter table,
  defaults, loader mechanics, and env-var names (Claims 1-3, 5-7) are settled
  and directly checkable against an installed CLI and a reachable `/rows`
  endpoint. It is not `settled` because the page carries no measured latency,
  throughput, failure-rate, or cost figures, and the three load-bearing
  absence-based findings (no revision pin, no documented fetch retry, the
  upstream degradations promptfoo does not surface) plus the cross-loader
  case-count divergence are the Miner's bounded inferences.
- `date_published` uses the page's "Last updated on Sep 30, 2026 by Michael"
  footer (the prose page carries no publication date); `date_extracted` and
  `last_checked` are today's UTC date.
- Per the Prospector's scoping in the triage comment, this note is deliberately
  **not** a general "promptfoo can import HF datasets" summary. It extracts the
  concrete `split`/`config`/`limit` surface with defaults, the three
  env-var names, the `/rows` + 100-row + `unlimited` pagination mechanics, and
  the variable-expansion override as a checkable reference, then layers the
  operational traps (empty-suite fail-open, rate-limit-scoped credential,
  `config.env` in the vendor's own example, unpinnable remote input) on top.
  The low-novelty triage assessment is respected in that Claim 1 is the only
  descriptive/ergonomic claim and everything else is a trap or a dependency
  property.
- **Candidate handling** (from `miner-related-notes.md`, read before writing
  Cross-References; the ten lexical-retrieval candidates are suggestions only —
  each is cited or dismissed by name below):
  - `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates + Extends,
    its Claims 8 and 10). The only genuinely on-topic candidate: same vendor,
    same HuggingFace dependency theme.
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology and
    SDLC phases; same vendor and same gating domain, but it carries no
    test-source-loading content; dismissed.
  - `docs-litellm-batches-api.md` — LiteLLM batch-file rate-limit accounting.
    Retrieved on the "unbounded fetch / 429" lexical overlap, but it is a
    different vendor and a different object (batch inference files, not an
    eval dataset loader); dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — SRE-Agent incident triage and
    LLM-as-judge eval alerts; no dataset-loading surface; dismissed.
  - `docs-promptfoo-javascript-assertions.md` — custom-JS assertion surface;
    retrieved on the sibling-page lexical match. Related to this note only via
    `docs-promptfoo-deterministic-metrics.md` Claim 12's trace-guard finding
    (open contradiction #1307), which is not this page's subject; dismissed.
  - `docs-promptfoo-pi-scorer.md` — the `pi` scorer credential pattern
    (`WITHPI_API_KEY`, a third-party console key). Same *shape* as this note's
    Claim 6 (a loader needing a vendor-issued key) and a possible future
    cross-ref, but it documents no HF dataset path and this note's CI-credential
    rule is already carried by #1288 Claim 8; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse's docs MCP server; unrelated vendor
    surface; dismissed.
  - `docs-google-sre-team-lifecycles.md` — SRE team org/lifecycles; no
    eval-gate or dataset content; dismissed.
  - `blog-promptfoo-red-team-claude.md` — per-model red-team plugin config
    (`reasoning-dos`, `budget_tokens`); the only link to this page is that the
    HF loader also feeds red-team corpora (BeaverTails example, cited in Guide
    Impact), which that note does not discuss; dismissed.
  - `docs-promptfoo-llm-rubric.md` — model-graded audio-grading surface;
    no test-source-loading content; dismissed.
  - The strongest cross-refs (`docs-promptfoo-dataset-generation.md`,
    `docs-promptfoo-configuration-guide.md`, `docs-promptfoo-configuration-caching.md`,
    `docs-promptfoo-deterministic-metrics.md`) were found by searching
    `source-notes/` per MINER.md §4 and the Prospector's overlap list, not by
    the lexical retrieval file.
- `registry/sources.json` and `registry/claims-index.json` were **not** edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.