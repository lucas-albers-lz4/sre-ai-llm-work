---
source_url: https://www.promptfoo.dev/docs/configuration/scenarios
source_type: docs
title: "Scenario Configuration - Grouping Tests and Data"
author: Promptfoo (page last updated by mldangelo-oai)
date_published: 2026-10-02
date_extracted: 2026-10-03
last_checked: 2026-10-03
status: current
confidence_overall: emerging
issue: "#1560"
---

# Scenario Configuration - Grouping Tests and Data

> Adds the test-suite *organization* layer the corpus's promptfoo cluster was
> missing: a `config` (rows) × `tests` (shared assertions) matrix that expands
> one assertion set into N cells, plus the `file://` + glob file composition
> that organizes large suites — and, read against the shipped loader, the
> position-dependent glob behavior that decides whether a renamed scenario file
> fails your pipeline loudly or silently shrinks the suite.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo `Configuration >
  Scenarios`, sidebar_position 13)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the tool's own config surface — authoritative
  for the config grammar, which is directly checkable against the published
  JSON schema and the shipped loader. The page is **entirely design-intent**:
  it carries no measured runtime, no cost figures, no CI-integration
  guidance, no failure data, and no validation of the matrix pattern in
  practice. Where this note reasons about cost, observability, or failure
  modes, those are explicitly marked as our assessment and are either
  attributed to a sub-page or verified against `promptfoo/promptfoo` @ `main`.
- **Scope**: Covers the `scenarios` array shape, the `Scenario` schema table,
  the translation example, external `file://` loading, and glob patterns with
  flattening. Does **NOT** cover: how many provider calls a matrix actually
  costs, how a matrix is named or filtered in output, what happens when a glob
  matches nothing, how scenarios interact with `prompts`/`providers`
  multiplication, or any CI-gating pattern. Those silences are themselves the
  substance of Claims 2, 5, 7, 8, and 10.
- **Last updated**: Oct 2, 2026 by `mldangelo-oai`.
- **Issue provenance**: auto-filed from the `promptfoo-docs` site-crawl seed
  (`https://www.promptfoo.dev/docs/getting-started/`); no human deep-read
  preceded this extraction. Triaged three times by the Prospector, all three
  agreeing `triaged:text` / `medium` / Ch05-primary. Duplicate check confirmed
  no existing note or open issue covers `configuration/scenarios`; #1513/#1543
  cover the configuration index and parameters, not this option.

## Extracted Claims

### Claim 1: `scenarios` is a two-part matrix — `config` supplies an array of variable sets and `tests` supplies one shared `TestCase[]` run against every one of them — and the page frames it as a *substitute* for hand-written tests, not an addition to them
- **Evidence**: the page's opening paragraph, the "Instead of creating
  individual tests" framing sentence, and the two bullet definitions of
  `config` and `tests`.
- **Confidence**: settled (documented product behavior; the expansion is
  stated in the page's own words)
- **Quote**: "The `scenarios` configuration lets you group a set of data along with a set of tests that should be run on that data." / "Instead of creating individual `tests` for each combination, we can create a `scenarios` that groups this data and the tests/assertions together:" / "`config`: an array of `vars` objects. Each `vars` object represents a set of variables that will be passed to the tests." / "`tests`: an array of `TestCase` objects. These are the tests that will be run for each set of variables in the `config`."
- **Our assessment**: Buy it — and the "Instead of" framing is the load-bearing
  clause, because it means the matrix is a compression of the config, not an
  addition to the suite. The compression ratio is the whole value proposition:
  the page's worked example is 3 language rows × 3 phrase tests = 9 cells
  written as 6 var keys plus 3 test blocks instead of 9 fully-spelled test
  cases. For a guide this is the concrete answer to "how do you organize an
  eval suite that has more than a handful of cases" — the answer is *not* more
  YAML, it is a second axis. Note carefully what the construct does **not**
  buy, though: it deduplicates the *assertion blocks*, not the *data*. Each
  row must still spell out its own expected values (Claim 4), so a 30-language
  matrix is 30 × (1 + expected-value-count) lines of vars. This is not free
  authoring; it is cheaper authoring.

### Claim 2: `description` is the only optional field on a `Scenario`, so the scenario *group* is unlabelled by default — and the only identifier any generated cell inherits is the inner test's own `description`
- **Evidence**: the `Scenario` schema table's Required column and Description
  column, read against the worked example, where the scenario object carries no
  `description` while all three inner tests do.
- **Confidence**: settled (the schema is explicit; the inheritance consequence
  is our reading of the example)
- **Quote**: "description | `string` | No | Optional description of what you're testing" / "config | `Partial<TestCase>[]` | Yes | An array of variable sets. Each set will be run through the tests." / "tests | `TestCase[]` | Yes | The tests to be run on each set of variables."
- **Our assessment**: Buy the schema; take the consequence seriously, because
  this is the page's most consequential omission. In the worked example the
  nine generated cells are named only `Translated Hello World` /
  `Translated Good Morning` / `Translated How are you?` — the language, which
  is the entire dimension the matrix varies, appears **nowhere** in any test
  identifier. So the three Spanish cells, three French cells, and three German
  cells share three names. Cross-referenced against
  `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 2** (verified),
  which documents promptfoo's JUnit contract as "one `<testcase>` per eval
  result" with `name` drawn from the test description: that note's coverage
  guarantee ("every promptfoo test appears in CI") is real — all nine cells
  *do* appear — but three of them now arrive under the same name, with the
  disambiguating var living only in the full export that Claim 4 of that note
  says CI is not supposed to carry. This is a concrete leak in a guarantee the
  corpus already treats as load-bearing, and it is a *silent* leak: nothing
  warns, nothing dedupes, nothing truncates. The actionable rule for a guide
  is that a scenario matrix used as a CI gate **must** put the varying
  dimension into the name — either via the scenario's `description` or into each
  test's — because the matrix's whole purpose is to vary something, and the
  harness will not tell you which something a given failure was.

### Claim 3: The schema types the row side as `Partial<TestCase>[]`, not a bare vars map — a much wider contract than the page's own prose, which narrows it to "an array of `vars` objects"
- **Evidence**: the `config` row of the schema table (type and description
  columns) set against the bullet immediately above it; every worked example on
  the page uses only `vars:` inside a `config` row.
- **Confidence**: settled as a documented type/prose mismatch; **emerging** as
  a risk, because the page does not say what happens if other `TestCase` fields
  appear in a `config` row
- **Quote**: "config | `Partial<TestCase>[]` | Yes | An array of variable sets. Each set will be run through the tests." (schema table) / "`config`: an array of `vars` objects." (prose bullet)
- **Our assessment**: Buy the mismatch as a finding, not as a bug claim — we
  did not verify runtime behavior for a non-`vars` key in a `config` row. The
  gap matters because `Partial<TestCase>` is a wide type: a reader who wants
  per-row `metadata` (the corpus's organization mechanism per
  `docs-promptfoo-modular-configs.md` **Claim 9**-adjacent guidance and
  `docs-promptfoo-configuration-huggingface-datasets.md` **Claim 1**) or a
  per-row `assert` override has no documented statement of whether the row
  wins over the shared test, is ignored, or is silently dropped. Under a
  *narrow* contract that is a small surprise; under the *declared* contract it
  is unspecified behavior in a construct whose entire value is that one block
  applies to many rows. The honest guide phrasing is "put `vars` in `config`;
  do not rely on other `TestCase` fields there — the page does not say what
  they do." Note also that the type is `Partial<TestCase>` rather than
  `Record<string, string>`, so values in a scenario row are **not**
  type-constrained to strings — which matters for Claim 6.

### Claim 4: What makes one assertion set reusable across rows is `{{var}}` interpolation into `assert[].value` — the assertions are the same *template*, not the same *value*, and that distinction is the entire mechanism
- **Evidence**: the three `assert` blocks in the worked example, each
  interpolating a different expected-value var, plus the page's statement that
  the same assertions run on each combination.
- **Confidence**: settled (the mechanism is fully visible in the example)
- **Quote**: "This will generate a matrix of tests for each language and input phrase combination, running the same set of assertions on each."
- **Our assessment**: Buy it, and note that the page's phrasing ("the same set
  of assertions") is technically true and operationally misleading. The three
  assertions differ in their *expected value* per row — `value:
  '{{expectedHelloWorld}}'` resolves to `'Hola mundo'` on the Spanish row and
  `'Bonjour le monde'` on the French row. "Same assertions" means same
  *shape and type and threshold*, not same *target*. This is what makes the
  matrix worth building and it is the reason the construct cannot be replaced
  by an array var (Claim 6). It also creates a failure mode the page does not
  mention and that we verified in the shipped code: the interpolation is
  non-strict. `getNunjucksEngine`'s `throwOnUndefined` parameter defaults to
  `false` in `src/util/templates.ts` (promptfoo @ `main`, read 2026-10-03) and
  no caller in the repo passes `true`, so an unresolved template variable
  renders to the **empty string**. `handleSimilar` in `src/assertions/similar.ts`
  then accepts it: its invariants reject only a non-string/non-array value and
  an empty *array* — `invariant(typeof renderedValue === 'string' ||
  Array.isArray(renderedValue), ...)` — and an empty *string* passes both. So
  renaming `expectedHelloWorld` to `expectedHello` in one `config` row does not
  fail the config load and does not error the assertion; it compares the model's
  output against `''`. That is a **silent** degradation of a gate, introduced by
  a one-character rename, in the exact construct whose purpose is to have one
  expected-value name shared across many cells.

### Claim 5: The page presents the matrix as the cost, but the real multiplication is matrix × prompts × providers — and the vendor's own shipped example for this page runs 3 providers × 2 prompts over the 9-cell matrix
- **Evidence**: the page's "3×3" framing; the example repository's config
  files, which the page links as "The full source behind this sample"; and the
  Test Cases page's cross-product statements.
- **Confidence**: settled for each component (the page's framing, the example
  config's contents, and the documented cross-product defaults are all
  directly readable); **emerging** for the combined arithmetic, which is ours
- **Quote**: "This will generate a matrix of tests for each language and input phrase combination, running the same set of assertions on each." (Scenarios page)
- **Quote** (Test Cases page, `/docs/configuration/test-cases/`, §Filtering
  Tests by Prompt / §Filtering Tests by Provider): "By default, each test runs
  against all prompts (a cartesian product)." / "**No filter**: Without the `providers` field, the test runs against all providers (cross-product behavior)"
- **Our assessment**: The page's numbers are the matrix only, and a reader who
  budgets CI cost off this page will be wrong by a factor of
  `prompts × providers`. Worked from the shipped example the page points at
  (`examples/config-multiple-translations/promptfooconfig-scenarios.yaml`,
  which lists `providers: openai:gpt-4.1-mini, openai:gpt-4.1,
  anthropic:claude-sonnet-5` and `prompts: - file://prompts.txt`, where
  `prompts.txt` contains two `---`-separated prompts): 3 rows × 3 tests = 9
  cells, × 2 prompts × 3 providers = **54 provider calls**, not 9. Two
  consequences worth stating. (a) The suite-size growth is multiplicative in
  three independent axes, and the scenarios page documents one of them. (b)
  The per-cell assertion is `type: similar`, which per
  `source-notes/docs-promptfoo-similar-assertion.md` **Claim 1** (verified)
  is not a local string check — its default embedding provider is OpenAI's
  `text-embedding-3-large`, "an unpinned, remotely-hosted dependency." So each
  of the 54 cells also implies an embedding call. The "cheap deterministic
  metric" reading of `similar` is wrong, and a guide that recommends the
  scenario matrix *because* its assertions are local would be recommending the
  opposite of the truth. Both numbers here are ours, computed from the
  published example files; neither the Scenarios page nor the Test Cases page
  performs this multiplication.

### Claim 6: `scenarios` is the hand-written alternative to array-var cartesian expansion, and the two produce different case counts *and different assertion costs* for the same logical data — which is why the vendor's own example pair diverges on assertion type
- **Evidence**: the two configs in the example repository the page links
  (`promptfooconfig-scenarios.yaml` and `promptfooconfig.yaml`), which cover
  different data with different mechanisms; and the Test Cases page's
  documented expansion behavior.
- **Confidence**: settled for the two configs and the expansion default
  (both directly readable); **emerging** for the "different assertion cost"
  reading, which is our synthesis
- **Quote** (Test Cases page, §Passing Arrays to Assertions): "By default,
  array variables expand into multiple test cases."
- **Our assessment**: The example repository is the most valuable artifact this
  page links, and the page does not use it that way — it presents only the
  scenario half. Read as a pair, the two configs make the construct's real
  advantage concrete. `promptfooconfig.yaml` declares
  `language: [French, German, Spanish, Italian, Portuguese, Portuguese]`-style
  *arrays* (6 languages) and `input:` as a 5-element array, relying on array
  expansion for 30 cases — and because an expanded array carries **one**
  assertion block for all 30, that block has to be a judge:
  `type: llm-rubric, value: 'Is this a correct translation of "{{input}}" into
  {{language}}? Score 1-5 where 5 is perfect.', threshold: 0.7`. The scenario
  config instead writes 3 explicit rows and can therefore use
  `type: similar, threshold: 0.90` against a per-row expected string. That is
  the real trade: **an array can only vary data under one shared assertion; a
  scenario can vary data under a per-row-varying assertion value.** So the
  matrix is not primarily a config-shorthand feature — it is the only one of
  these two mechanisms that lets you assert against *different* expected
  answers without a model-graded judge in the loop. (Caveat on our own
  reading: per Claim 5 the `similar` path is not free either, since it calls
  an embedding provider; the saving is against `llm-rubric`'s per-cell *judge*
  call, not against zero cost.) Cross-referenced against
  `source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
  **Claim 4** (verified), which establishes a *third* case-count semantic — HF
  rows arrive with array expansion switched off — so the corpus now has three
  loaders (`file://` YAML, inline array vars, `huggingface://`) yielding three
  different case counts for the same logical rows. A guide statement about
  "how many tests does this suite have" cannot be loader-independent.

### Claim 7: Glob patterns load many scenario files and flatten them into one array, but the page promises no per-file provenance, no ordering guarantee, and no dedupe — so the directory structure it recommends as an organization scheme survives only in the config, never in the run
- **Evidence**: the three glob forms, the flattening sentence, the recommended
  `unit/` vs `integration/` tree, and the mixing example — read against the
  loader's flattening step.
- **Confidence**: settled for the flattening and for the absence of any
  provenance/ordering/dedupe statement; **emerging** for the consequence
- **Quote**: "When using glob patterns, all matched files are loaded and their scenarios are automatically flattened into a single array. This is useful for organizing large test suites:" / "You can mix glob patterns with direct file references:" / "This functionality allows you to easily run a wide range of tests without having to manually create each one. It also keeps your configuration file cleaner and easier to read."
- **Our assessment**: Buy the flattening; be sharp about what it costs. The
  page's own recommended layout splits `scenarios/` into `unit/` and
  `integration/` subtrees, and its mixing example then shows selecting one of
  them (`- file://scenarios/unit/*.yaml`) — which implicitly promises that
  unit-ness is a selectable scope. It is not. Once a pattern like
  `file://scenarios/**/*.yaml` matches across both subtrees, the flattening
  step (a literal `.flat()` in `src/util/config/load.ts` on `main`, read
  2026-10-03) discards the grouping: from that point the run has one
  undifferentiated scenario array with no record of which file any scenario
  came from. The page documents no ordering guarantee, no dedupe behavior, and
  no tag injection from the filename or directory. So the directory layout is
  a *loading* convenience (it decides what a given glob picks up), not a
  *reporting* dimension. Cross-referenced against
  `source-notes/docs-promptfoo-modular-configs.md` **Claim 9** (verified),
  which is the corpus's existing answer to "how does a CI gate select a smoke
  vs full scope" — there it is an env-var branch inside the config that
  changes the provider set, the test directory, and the log level. Scenarios'
  globs offer a *narrower* mechanism for the same job: they change which files
  load, with none of that explicitness and none of the `--filter-metadata`
  scoping the Test Cases page documents. For a guide this is a real warning:
  **a `**/*.yaml` scenario glob silently destroys the unit/integration
  distinction the same page just taught you to build.**

### Claim 8: The two glob positions inside the same `scenarios` construct have **opposite** unmatched-glob behavior — the page's own documented glob form throws and aborts the run, while `scenario.tests` globs warn and contribute zero rows
- **Evidence**: the page's silence on the question, plus the two loader
  functions in `promptfoo/promptfoo` @ `main` (read 2026-10-03) and the two
  call sites that reach them.
- **Confidence**: settled (read directly from the shipped source; both
  functions quoted verbatim below)
- **Quote** (docs, on the subject — the page's *only* statement of unmatched-glob
  behavior anywhere in the promptfoo documentation set, from the Test Cases
  page, §Path Resolution, and it is scoped to test sources): "An unmatched
  test-source glob warns and adds no rows; a missing literal test file is an
  error."
- **Quote** (code — `src/util/file.ts`, the loader reached for the page's own
  documented `scenarios:` glob form, via `src/util/config/load.ts:1172` for a
  whole-key string and `:806` for each `file://` array entry):
  ```js
  const matchedFiles = globSync(pattern, {
    windowsPathsNoEscape: true,
  });

  if (matchedFiles.length === 0) {
    throw new Error(`No files found matching pattern: ${resolvedPath}`);
  }
  ```
- **Quote** (code — `loadTestsFromGlobWithEnv` in `src/util/testCaseReader.ts`,
  the loader reached for `scenario.tests` via `readTestSources` at
  `src/util/config/load.ts:1192`):
  ```js
  const message = `No test files found for path: ${resolvedPath}`;
  if (!hasGlobMagic(path.relative(path.resolve(basePath), resolvedPath))) {
    throw new Error(message);
  }
  logger.warn(message);
  return ret;
  ```
- **Our assessment**: This is the page's most consequential undocumented
  property, and it is the direct answer to the Prospector's third triage
  question (does a missing or renamed scenario file fail loudly or silently
  reduce coverage?). The answer is **both, depending on where the glob sits**,
  and the conditioning variable is invisible in the config a reviewer reads.
  The `scenarios:` position — the one this page documents at length, with three
  worked examples — **throws**, aborting the run with a clear message. The
  nested `scenario.tests:` position **warns and returns zero rows**, which is
  the silent-coverage-loss mode the corpus already flags as a gate that cannot
  fail (`source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
  **Claim 5**, verified). The page mixes both in one config in its own mixing
  example, so an operator following it has both failure modes in one file with
  nothing in the config to tell them apart. Note the third case for
  completeness: a glob whose *pattern contains no magic* throws in both
  positions (`hasGlobMagic` is false), so a literal missing path is always
  loud. The dangerous transition is specifically *magic → unmatched*, and
  specifically in the nested `tests` slot. Filed as contradiction issue
  **#1565**; see Cross-References. **No verdict is taken here** per MINER.md
  §4a.

### Claim 9: A single `threshold: 0.90` is applied across three languages whose expected strings differ in length and diacritics, on a metric whose shipped default the documentation never states
- **Evidence**: the three identical `threshold: 0.90` literals in the worked
  example, set against the three sets of expected values they gate; plus the
  sibling `similar` assertion page and the shipped default.
- **Confidence**: settled for the config contents and the shipped default;
  **emerging** as a brittleness claim, since the page offers no calibration
  rationale and no failure data
- **Quote**: "threshold: 0.90" (repeated verbatim on all three assertions in
  the worked example)
- **Our assessment**: The literal is unremarkable on its face; what makes it
  worth recording is that it is applied to a heterogeneous set with no stated
  basis. The three expected values are `'Hola mundo'` (10 chars),
  `'Comment ça va?'` (13), and `'Wie geht es dir?'` (15) — different lengths,
  and two carry diacritics or inversive punctuation (`'¿Cómo estás?'`,
  `'Comment ça va?'`). Per `source-notes/docs-promptfoo-similar-assertion.md`
  **Claim 1** (verified), `similar` defaults to cosine over OpenAI
  `text-embedding-3-large`, an unpinned remotely-hosted model; per that note's
  **Claim 2** (verified) the metric is invisible in the compact
  `similar(0.8):value` form and the type string here is bare `similar`, so the
  metric is cosine *by default and by omission*. Per that note's **Claim 9**
  (verified), the docs page states no default threshold in any metric. We
  resolved that gap from the shipped source: `src/assertions/similar.ts` has
  `const threshold = assertion.threshold ?? 0.75;`. Two things follow. First,
  the `0.90` here is a deliberate author choice (the sibling page uses `0.8`
  in four of its five examples) with **no** stated rationale, no per-language
  calibration, and no reported pass rate — so a reader cannot tell whether
  `0.90` is a validated operating point or a round number. Second, the shipped
  `0.75` default is a *worse* value than `0.8`, and it is undocumented: an
  operator who drops the `threshold` line from a scenario matrix silently gets
  a looser gate than either number on either page. **This supplements rather
  than contradicts** `docs-promptfoo-similar-assertion.md` Claim 9 (the docs are
  silent, not wrong), so per MINER.md §4a it is recorded here and in #1565's
  context rather than filed separately — but the guide should now have a
  concrete number for that note's previously-open question.

### Claim 10: The page's entire statement about what scenarios cost is one sentence about ergonomics — there is no runtime, cost, rate-limit, or CI guidance anywhere on it, and the corpus already documents that promptfoo has no token-rate control
- **Evidence**: the closing sentence of the page, set against the absence of
  any cost/runtime/rate-limit content on the page.
- **Confidence**: settled as a documented absence; the cost consequence is ours
- **Quote**: "This functionality allows you to easily run a wide range of tests without having to manually create each one. It also keeps your configuration file cleaner and easier to read."
- **Our assessment**: "Easily run a wide range of tests" is the whole of the
  vendor's cost position, and it is a statement about YAML ergonomics being
  read as a statement about scale. Three corpus facts make that reading unsafe
  for a guide. (a) Per `source-notes/docs-promptfoo-configuration-rate-limits.md`
  **Claim 12** (verified), promptfoo's rate-limit control surface is "a
  *concurrency* count" with "no documented token-rate or request-rate control"
  — so the only lever against a 54-call matrix is how many run at once, not how
  many run. Per that note's **Claim 3** (verified), concurrency is AIMD and
  reactive. (b) Per `source-notes/docs-promptfoo-configuration-caching.md`
  **Claim 1** (verified), provider results are cached on disk by default, and
  per **Claim 4** (verified) entries live up to a 14-day TTL — so a scenario
  matrix that is green may be substantially replayed from cache, measuring
  responses up to two weeks old. (c) The largest per-cell cost in this
  construct may be the embedding call, and
  `source-notes/docs-promptfoo-similar-assertion.md` **Claim 1** (verified)
  explicitly records that it is **unknown** whether the `similar` embedding call
  is subject to that cache — that note flags the gap and this page's
  construction is the case where it bites, since `similar` is the assertion
  type the page's own example uses. The guide should not repeat the ergonomic
  claim as a scale claim. State instead: a scenario matrix's cost is
  `rows × tests × prompts × providers`, plus whatever per-cell assertion type
  implies, and it is subject to a 14-day cache whose interaction with the
  example's own assertion type is undocumented.

## Concrete Artifacts

### The complete worked example (verbatim from the Scenarios page, §Example)

The page renders the prompts file and the config; both are reproduced exactly,
with line breaks as they appear in the page.

```
# prompts.txt
You're a translator. Translate this into {{language}}: {{input}}
---
Speak in {{language}}: {{input}}
```

```
# promptfooconfig.yaml
scenarios:
  - config:
      - vars:
          language: Spanish
          expectedHelloWorld: 'Hola mundo'
          expectedGoodMorning: 'Buenos días'
          expectedHowAreYou: '¿Cómo estás?'
      - vars:
          language: French
          expectedHelloWorld: 'Bonjour le monde'
          expectedGoodMorning: 'Bonjour'
          expectedHowAreYou: 'Comment ça va?'
      - vars:
          language: German
          expectedHelloWorld: 'Hallo Welt'
          expectedGoodMorning: 'Guten Morgen'
          expectedHowAreYou: 'Wie geht es dir?'
    tests:
      - description: Translated Hello World
        vars:
          input: 'Hello world'
        assert:
          - type: similar
            value: '{{expectedHelloWorld}}'
            threshold: 0.90
      - description: Translated Good Morning
        vars:
          input: 'Good morning'
        assert:
          - type: similar
            value: '{{expectedGoodMorning}}'
            threshold: 0.90
      - description: Translated How are you?
        vars:
          input: 'How are you?'
        assert:
          - type: similar
            value: '{{expectedHowAreYou}}'
            threshold: 0.90
```

Read this config for what it does *not* say: the scenario block has no
`description`, so the only names in the resulting 9-cell matrix are
`Translated Hello World`, `Translated Good Morning`, and
`Translated How are you?` — three names for nine cells (Claim 2). And there is
no `prompts:` or `providers:` key, so per the Test Cases page's documented
cross-product defaults the cells multiply by whatever the rest of the project
supplies (Claim 5).

### The Scenario schema (verbatim from the page's §Configuration table)

| Property | Type | Required | Description |
| --- | --- | --- | --- |
| description | `string` | No | Optional description of what you're testing |
| config | `Partial<TestCase>[]` | Yes | An array of variable sets. Each set will be run through the tests. |
| tests | `TestCase[]` | Yes | The tests to be run on each set of variables. |

### External loading and glob patterns (verbatim from §Configuration and §Using Glob Patterns)

```yaml
# External file reference
scenarios:
  - file://path/to/your/scenario.yaml
```

```yaml
# Glob patterns
scenarios:
  - file://scenarios/*.yaml # All YAML files in scenarios directory
  - file://scenarios/unit-*.yaml # All files matching unit-*.yaml
  - file://scenarios/**/*.yaml # All YAML files in subdirectories
```

```
# The recommended directory layout (verbatim from the page)
scenarios/
├── unit/
│   ├── auth-scenarios.yaml
│   └── api-scenarios.yaml
└── integration/
    ├── workflow-scenarios.yaml
    └── e2e-scenarios.yaml
```

```yaml
# Mixing globs with direct references — note both positions in one list
scenarios:
  - file://scenarios/critical.yaml # Specific file
  - file://scenarios/unit/*.yaml # All unit test scenarios
```

### The two loader functions behind Claim 8 (verbatim from `promptfoo/promptfoo` @ `main`, read 2026-10-03)

These are quoted in full in Claim 8. The load graph that makes the difference
observable, for a resolver or a reader who wants to re-verify:

```
scenarios: - file://scenarios/*.yaml
  -> src/util/config/load.ts:806  (file:// entry in the scenarios array)
     or :1172 (whole scenarios value is a string)
  -> maybeLoadFromExternalFile()   src/util/file.ts:82
  -> globSync(); if zero matches -> throw            <-- FAIL-LOUD

scenario:
  tests:
    - file://tests/*.yaml
  -> src/util/config/load.ts:1192 (scenario.tests is an array)
  -> readTestSources()              src/util/config/load.ts:550
  -> loadTestsFromGlobWithEnv()     src/util/testCaseReader.ts:611
  -> zero matches + hasGlobMagic -> logger.warn; return []  <-- SILENT
  -> zero matches + no magic       -> throw
```

### The vendor's own paired configs (verbatim from `examples/config-multiple-translations`, which the Scenarios page links as "The full source behind this sample")

Fetched 2026-10-03 from
`https://raw.githubusercontent.com/promptfoo/promptfoo/main/examples/config-multiple-translations/`.
This pair is the artifact that makes Claim 6 concrete, and the page only ever
shows the first file's content.

```yaml
# promptfooconfig-scenarios.yaml  (excerpt: the parts that differ from the array form)
description: Scenario-based translation with expected results

prompts:
  - file://prompts.txt

providers:
  - openai:gpt-4.1-mini
  - openai:gpt-4.1
  - anthropic:claude-sonnet-5

scenarios:
  - description: Translation accuracy with expected results
    config:
      - vars:
          language: Spanish
          expectedHelloWorld: 'Hola mundo'
          # ... (French and German rows as on the docs page)
    tests:
      - description: Translated Hello World
        vars:
          input: 'Hello world'
        assert:
          - type: similar
            value: '{{expectedHelloWorld}}'
            threshold: 0.90
```

```yaml
# promptfooconfig.yaml  (the default config for the same example — array-based)
description: Array-based multi-language translation testing

prompts:
  - file://prompts.txt

providers:
  - openai:gpt-4.1-mini
  - openai:gpt-4.1
  - anthropic:claude-sonnet-5

tests:
  - vars:
      language:
        - French
        - German
        - Spanish
        - Italian
        - Portuguese
      input:
        - 'Hello world'
        - 'Good morning'
        - 'How are you?'
        - 'Thank you very much'
        - 'See you later'
    assert:
      - type: llm-rubric
        value: 'Is this a correct translation of "{{input}}" into {{language}}? Score 1-5 where 5 is perfect.'
        threshold: 0.7
```

The pair, read together: the array form covers 6 languages × 5 phrases = 30
cases but can only assert one way, so it uses a judge
(`llm-rubric`, `threshold: 0.7`) for all 30. The scenario form covers 3
languages × 3 phrases = 9 cases and asserts against a per-row expected string
with `similar`. Different data, different coverage, different assertion cost —
and the page presents only the second. Note also that the example's own
`README.md` treats them as interchangeable run modes
(`promptfoo eval` vs `promptfoo eval -c promptfooconfig-scenarios.yaml`),
which is a coverage difference, not a style difference.

### The shipped `similar` threshold default (verbatim from `src/assertions/similar.ts`, @ `main`, read 2026-10-03)

```js
const threshold = assertion.threshold ?? 0.75;
```

and the invariants that let an empty rendered value through (Claim 4):

```js
invariant(
  typeof renderedValue === 'string' || Array.isArray(renderedValue),
  'Similarity assertion type must have a string or array of strings value',
);
invariant(
  !Array.isArray(renderedValue) || renderedValue.length > 0,
  'Similarity assertion must have at least one value to compare against',
);
```

Note the asymmetry: an empty **array** is rejected; an empty **string** — which
is what an unresolved `{{var}}` produces — is not.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-configuration-outputs.md` **Claim 2**
    ("The JUnit structural contract is one `<testsuite>` per prompt/provider pair
    and one `<testcase>` per eval result — so grouping and per-case coverage are
    explicit design requirements, not incidental"). Verified by re-reading the
    note. This page is where that guarantee gets its first visible strain:
    per Claim 2, three names cover nine cells, so the coverage guarantee holds
    at the row level while the *naming* that makes a CI dashboard legible stops
    distinguishing the dimension the matrix exists to vary. The two notes
    compose into one guide rule — a scenario matrix must surface its varying
    dimension in the test name, because the JUnit format will faithfully
    publish whatever name it is given, three times over.
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
    **Claim 5** ("`split` defaults to `test` and the documented symptom of
    getting it wrong is **empty results**, not an error — a wrong split or
    config yields a zero-case eval, which is a CI gate that passes without
    testing anything"). Verified by re-reading the note. That note's finding —
    a promptfoo config mistake that is *not visible in the config* and yields a
    zero-case green gate — is confirmed here on a second, independent axis
    (Claim 8, nested `scenario.tests` glob) and gains a new sibling on a third
    (Claim 4, a renamed expected-value var degrading to `similar` against
    `''`). Three distinct silent-green mechanisms now attach to eval-suite
    construction rather than to loader settings, which is the argument for
    promoting that note's recommendation from a loader caveat to a
    pipeline-wide invariant.
  - `source-notes/docs-promptfoo-configuration-huggingface-datasets.md`
    **Claim 4** ("Variable expansion is switched off for HF-loaded rows ...
    so the same logical dataset yields different case counts depending on which
    loader fetched it"). Verified by re-reading the note. That note established
    two case-count semantics; this page adds the third (Claim 6) and, unlike
    either of the others, the scenarios semantics is the one an operator
    chooses *deliberately* in their own YAML rather than inheriting from a
    loader default. The three-way agreement on "case count is a function of the
    mechanism, not just the data" is now strong enough to state as a guide
    rule.
  - `source-notes/docs-promptfoo-similar-assertion.md` **Claim 1** ("The
    `similar` assertion is a model-assisted gate whose default embedding
    provider is OpenAI's `text-embedding-3-large` — an unpinned,
    remotely-hosted dependency in a suite that otherwise looks like string
    matching"), **Claim 2**, and **Claim 9**. All three verified by re-reading
    the note. This page is the construct that makes `similar` a *scaling*
    decision rather than a per-assert one: the same assertion type is stamped
    across `rows × tests × prompts × providers` cells, so an unpinned embedding
    dependency becomes a suite-wide exposure, and an undocumented threshold
    default becomes a suite-wide looseness. That note's **Claim 9** also
    recorded its default-threshold question as unanswerable from
    documentation; Claim 9 of this note answers it from the shipped source
    (`0.75`).

- **Contradicts** (filed by this note, per MINER.md §4a):
  - Issue **#1565** (open, `contradiction` + `needs-resolution`) — "promptfoo
    unmatched-glob semantics are position-dependent: `scenarios:` /
    `file://scenario.yaml` globs **throw**, while `scenario.tests:` globs
    **warn and add zero rows** — opposite failure modes for the same syntax".
    **Side A** is
    `source-notes/docs-promptfoo-configuration-huggingface-datasets.md` Claim 5
    (a promptfoo test-source mistake yields empty results, i.e. a green gate
    that tested nothing). **Side B** is this page plus the shipped loader: the
    page's own documented glob form throws, while the nested `scenario.tests:`
    glob warns — so the silent-green mode is real for one position and
    impossible for the other, and the docs state neither. Both sides are quoted
    verbatim in #1565 and in Claim 8 here. **No verdict is taken in this note**,
    per MINER.md §4a; the safe interim rule (assert a non-zero scenario count
    before interpreting a matrix gate) is stated in #1565 as the filer's
    recommendation only.
  - No other contradiction identified. Verified against `CONTRADICTIONS.md` (no
    `C-NNN` entries appended yet) and against all 13 open
    `contradiction`-labeled issues (`#1562`, `#1550`, `#1548`, `#1534`,
    `#1517`, `#1514`, `#1486`, `#1462`, `#1461`, `#1408`, `#1352`, `#1338`,
    `#1322`, `#1307`, `#1150`). The live tension with
    `docs-promptfoo-similar-assertion.md` Claim 9 (docs state no default
    threshold; the shipped default is `0.75`) is **not** filed: that is an
    omission in one page rather than two sources disagreeing, which is
    explicitly a do-not-file case under MINER.md §4a. It is recorded in Claim 9
    and repeated as context in #1565. Two other tensions were considered and
    rejected as contradictions: (a) `scenarios:` globs throwing vs the page's
    silence — an omission, not opposition, and it is folded into #1565 as the
    docs-side of a real position-dependent behavior rather than filed twice;
    (b) `**/*.yaml` flattening erasing the `unit/`/`integration/` distinction —
    this is one page underselling its own mechanism (Claim 7), not two sources
    disagreeing.

- **Extends**:
  - `source-notes/docs-promptfoo-modular-configs.md` — the sibling page on
    `file://` composition of top-level keys. Three extensions, all verified by
    re-reading the note:
    (a) **Claim 1** states that `file://` is accepted on "each of the four
    top-level keys (`prompts`, `providers`, `tests`, `defaultTest`)". The
    Scenarios page establishes a **fifth** top-level key with the same
    `file://` mechanism plus glob support, and — per Claim 8 — with
    *different* unmatched-glob semantics than `tests:`. So the corpus's mental
    model of "how a promptfoo config is composed from files" needs a
    per-key column, not a single rule.
    (b) **Claim 2** (`tests:` accepts a list of *directory* paths) is the
    existing precedent for directory-based suite composition; Scenarios offers
    globs instead, which is strictly less informative about what loaded (Claim
    7).
    (c) **Claim 9** (suite scope selected by `process.env.TEST_MODE`, with the
    two branches differing in provider set, test directory, log level, and
    result retention) is the corpus's answer to smoke-vs-full CI gating. A
    scenario glob is the weaker version of the same lever, and Claim 7 explains
    why: the glob selects files but attaches no scope identity to what it
    loads. A guide recommending scenario globs for CI scope selection should
    say so *against* that note's more explicit mechanism.
  - `source-notes/docs-promptfoo-configuration-caching.md` — **Claim 1** (cache
    on disk by default) and **Claim 4** (14-day TTL, "cached responses can be
    replayed for up to two weeks after a provider silently changes model
    behavior"), both verified. Extends, because a scenario matrix is exactly the
    shape of suite that maximizes cache leverage — many cells, few distinct
    prompts, one config — so the matrix pattern makes the 14-day replay window
    more load-bearing, not less. Per Claim 10 the open question is whether the
    matrix's dominant per-cell cost (the `similar` embedding call) is cached at
    all; `docs-promptfoo-similar-assertion.md` Claim 1 records that as unknown.
  - `source-notes/docs-promptfoo-configuration-rate-limits.md` — **Claim 3**
    (AIMD concurrency: "cut concurrency by 50% when a rate limit is hit, add 1
    after sustained successful requests") and **Claim 12** ("the page's entire
    control surface is a *concurrency* count — there is no documented
    token-rate or request-rate control"), both verified. Extends: these supply
    the missing cost model for the multiplication in Claim 5. The only lever
    against `rows × tests × prompts × providers` is how many cells run
    concurrently, and the concurrency controller is reactive, so a matrix that
    trips a limit spends wall-clock time backing off rather than fewer calls.
  - `source-notes/docs-promptfoo-chat-threads.md` **Claim 5** ("each unique
    `conversationId` maintains its own separate conversation history.
    Scenarios automatically isolate conversations by default"). Verified.
    Extends, and it is the only other corpus mention of `scenarios` at all:
    that note found the term in passing while documenting conversation
    isolation, and this page is the definition of the construct that provides
    it. Worth recording because it means a scenario matrix is *also* the
    isolation mechanism for multi-turn suites — a second use of the same
    construct that the Scenarios page never mentions, and one with a real
    interaction: isolation is keyed on the generated cell, so per Claim 2 an
    unnamed matrix gives the operator no handle to isolate or select a specific
    conversation.

- **Novel**: The first corpus source on **how a promptfoo eval suite is
  organized at the suite-construction layer**. Before this note,
  `grep -ril "scenarios" source-notes/` matched only
  `docs-promptfoo-chat-threads.md` (passing mention) and nothing about the
  config key. Specifically new:
  1. **The `config` × `tests` matrix as a distinct third case-count mechanism**,
     alongside inline array expansion and `huggingface://` loading, with the
     concrete consequence that it is the only one of the three that permits a
     *per-row-varying assertion value* (Claim 6). This is what lets an eval
     suite assert against per-row expected answers without a model-graded judge
     in the loop.
  2. **The observability cost of an unnamed matrix**: `description` is optional
     and unused in the vendor's own example, so N×M cells collapse onto M names
     in the JUnit artifact (Claim 2) — a concrete strain on
     `docs-promptfoo-configuration-outputs.md` Claim 2's coverage guarantee.
  3. **Two new silent-green mechanisms**: a renamed expected-value var degrading
     `similar` to a comparison against `''` via non-strict template rendering
     (Claim 4), and the position-dependent unmatched-glob split (Claim 8,
     filed as #1565).
  4. **`similar`'s shipped default threshold of `0.75`**, which closes the
     open question recorded at `docs-promptfoo-similar-assertion.md` Claim 9
     and which is looser than any literal on either page (Claim 9).
  5. **The multiplicative cost formula** `rows × tests × prompts × providers`
     with the vendor's own example config supplying 3 × 2 × 3 = 54 calls for a
     page that presents 9 (Claim 5).
  6. **The `unit/` vs `integration/` directory layout as a loading-only
     convention** — a `**/*.yaml` glob silently collapses the distinction the
     same page teaches (Claim 7).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — add a subsection on eval-suite
  construction, adjacent to the existing "Evaluation and measurement
  methodology" material (~line 386)**: the chapter currently discusses *which
  metrics* to trust and *whether a gate can fail*, but has nothing on how a
  suite larger than a handful of cases is organized. Add: a promptfoo
  `scenarios` block is a two-axis matrix where `config` rows supply variable
  sets and `tests` supplies one shared assertion block, and its distinguishing
  property is not config brevity but that **the assertion value can vary per
  row** — which is what lets a suite assert against per-row expected answers
  without an `llm-rubric` judge call per cell. Cite the vendor's own paired
  configs (`promptfooconfig.yaml` array form with `llm-rubric` vs
  `promptfooconfig-scenarios.yaml` with `similar`) as the evidence (Claim 6).
  Add the counter-rule from the same section: do not read "easily run a wide
  range of tests" as a scale claim — cost is `rows × tests × prompts ×
  providers` and the page documents one of those four axes (Claim 10, Claim 5).
- **Chapter 05 — add two rows to the "A gate that cannot fail is not a gate"
  table (~line 655), both marked as *not visible in the config* like the
  HuggingFace row**: (a) a `scenario.tests:` glob that matches nothing warns
  and contributes zero rows, so a renamed test file inside a scenario yields a
  green gate that tested nothing — cite `docs-promptfoo-configuration-huggingface-datasets.md`
  Claim 5 for the established precedent and this note's Claim 8 for the new
  position, cross-referencing contradiction **#1565** since the sibling
  `scenarios:` position throws and the guide must not state one behavior for
  both; (b) a renamed or misspelled expected-value var in a `config` row
  renders `assert[].value` to `''` and compares the model output against the
  empty string with no error at load time and no error at grade time (Claim 4).
  Neither is a config line a reviewer can spot in a diff, which is the
  property that makes them the right rows for this table. The existing rule in
  that section ("Can this gate fail? is a grep of the config") needs one
  sentence widened: it is now also a question about which *loader slot* a
  `file://` reference occupies and whether every `{{var}}` in an `assert[].value`
  resolves.
- **Chapter 05 — extend the caching / hermeticity discussion with the
  suite-shape interaction**: a scenario matrix maximizes cache leverage (many
  cells, few distinct prompts), so `docs-promptfoo-configuration-caching.md`
  Claim 4's 14-day TTL is more load-bearing for matrix suites, not less. State
  the open question honestly rather than resolving it: the matrix's dominant
  per-cell cost is the `similar` embedding call
  (`docs-promptfoo-similar-assertion.md` Claim 1), and whether that call is
  subject to the eval cache is **undocumented** (Claim 10).
- **Chapter 05 — extend the assertion-calibration material with a concrete
  threshold default**: `similar` ships with `threshold ?? 0.75`, which is
  documented nowhere and is looser than the `0.8` used in the sibling page's
  examples. A guide rule that follows: *every* assertion type needs its
  threshold written down explicitly in your own notes, because the vendor's
  shipped default is neither documented nor the tightest value the vendor
  demonstrates (Claim 9). This resolves a question Ch05 currently has to leave
  open.
- **Chapter 05 — CI scope selection, as a caution rather than a
  recommendation**: note that scenario globs look like a smoke-vs-full suite
  selector but are strictly weaker than the existing `TEST_MODE` config-branching
  pattern in `docs-promptfoo-modular-configs.md` Claim 9, and that a
  `**/*.yaml` glob silently collapses the `unit/`/`integration/` distinction
  the same page teaches (Claim 7). If the chapter recommends glob-based scope
  selection anywhere, it must say that the directory layout is a *loading*
  convention with no reporting-side identity.
- **Chapter 03 (Runbooks and Agents) — CI eval-pipeline runbook**: add the
  invariant "assert a non-zero (ideally minimum-expected) scenario count before
  interpreting a scenario-matrix gate's verdict," with the position caveat from
  #1565 (the `scenarios:` glob throws, the nested `tests:` glob does not), and
  the naming rule from Claim 2 (put the varying dimension in the test
  `description`, because the JUnit format will publish whatever name it is
  given once per cell).

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (`https://www.promptfoo.dev/docs/configuration/scenarios/`) **and** of its
  markdown source at
  `https://raw.githubusercontent.com/promptfoo/promptfoo/main/site/docs/configuration/scenarios.md`,
  which was used to guarantee verbatim quote fidelity — the rendered HTML
  extraction collapses code blocks to single lines, and the markdown source
  restores exact whitespace and the `title=` annotations. Per MINER.md §1, three
  linked resources were also read because claims depend on them, each
  attributed in-line rather than blended into the primary source:
  1. **`examples/config-multiple-translations`** — the page's own linked
     "full source behind this sample". All four files fetched raw
     (`README.md`, `prompts.txt`, `promptfooconfig.yaml`,
     `promptfooconfig-scenarios.yaml`). This produced Claims 5 and 6, which the
     docs page alone cannot support: the shipped configs carry `providers:`
     and `prompts:` keys the page's inline example omits, and the array-form
     sibling config is the concrete evidence for why the matrix construct
     exists at all.
  2. **Test Cases** (`/docs/configuration/test-cases/`, `pagination_prev`) —
     for the prompts/providers cross-product defaults (Claim 5), the
     array-expansion default (Claim 6), and the one documented statement of
     unmatched-glob behavior anywhere in the docs set (Claim 8). Read in full;
     most of it (CSV/XLSX columns, JSON/JSONL, Azure Blob, Google Sheets) is
     out of scope for this note and carries no scenarios-specific claim.
  3. **`promptfoo/promptfoo` @ `main`** (sparse checkout of
     `src/util/config/load.ts`, `src/util/file.ts`,
     `src/util/testCaseReader.ts`, `src/assertions/similar.ts`,
     `src/util/templates.ts`), read 2026-10-03 — for Claim 4 (non-strict
     template rendering and the empty-string acceptance in
     `handleSimilar`), Claim 7 (the literal `.flat()` flattening step), Claim 8
     (the two opposite loaders and their call sites), and Claim 9 (the
     `threshold ?? 0.75` default). Every code quotation in this note is verbatim
     from that checkout, and every one is attributed to its file in-line. No
     code claim is stated as a documentation claim.
  Not followed: `/docs/configuration/datasets/` (`pagination_next` — already
  covered by `docs-promptfoo-configuration-huggingface-datasets.md` and
  `docs-promptfoo-dataset-generation.md`), `/docs/configuration/reference/`
  (already covered per the issue's duplicate check: #1513/#1543), and the
  product/solutions/footer navigation links (marketing).
- **Prospector coverage.** All three triage comments are addressed. From the
  first: the schema shape, the 3×3 translation example and matrix behavior,
  external/glob loading with flattening/merge semantics, and the `unit/` vs
  `integration/` layout are Claims 1, 6, 7, and the Concrete Artifacts; the
  requested *implications* (multiplicative suite size, glob drift, brittle
  `similar` thresholds, cross-language expected-value drift) are Claims 5, 8,
  and 9, each explicitly marked as our assessment rather than page claims. From
  the second: (a) per-combination CI attribution is Claim 2 (the answer is the
  matrix collapses attribution — three names for nine cells); (b) glob
  flattening and per-file attribution is Claim 7, and the dedupe/ordering
  question is answered as *undocumented*; (c) whether glob loading is a
  config-load-time or run-time concern is answered in Claim 8 as config-load
  time, with the substantive finding that the two positions differ. From the
  third: the assertion-variable interpolation pattern and threshold handling
  are Claims 4 and 9. The second triage comment's framing — "design-intent
  rather than validated practice" — is adopted in Source Context and is why
  `confidence_overall` is `emerging`.
- **Candidate review** (from `miner-related-notes.md`, read before
  Cross-References per MINER.md §4; the file was **not** committed). Each of the
  10 candidates was cited or dismissed by name:
  1. `docs-promptfoo-pi-scorer.md` — **dismissed**. A model-graded scorer
     (`pi`, `WITHPI_API_KEY`, `0.5` default threshold). No matrix, suite-
     organization, or file-composition content. Its threshold-default theme
     echoes Claim 9 but is a different assertion type with a documented
     default, so citing it would be a thematic rather than evidential match.
  2. `docs-google-sre-team-lifecycles.md` — **dismissed**. Google SRE org
     design (hiring, team topology, SLOs-with-consequences). Nothing about
     eval-suite construction.
  3. `blog-promptfoo-owasp-red-teaming.md` — **dismissed**. Sets the *policy*
     that red teaming belongs in CI; this page is a config-mechanics note with
     no CI-process recommendation to corroborate. (Contrast
     `docs-promptfoo-configuration-outputs.md`, whose claims genuinely do
     extend that blog — cited there, not here.)
  4. `docs-litellm-batches-api.md` — **dismissed**. The lexical match is on
     batch/rate-limit vocabulary. Related in *spirit* — that note is about
     bounding request cost, which is what Claim 10 is reaching for — but the
     corpus already has the on-vendor source for that
     (`docs-promptfoo-configuration-rate-limits.md`, cited in Claim 10), so
     citing the cross-vendor note here would be a weaker, indirect citation.
  5. `blog-pagerduty-sre-agent-triage.md` — **dismissed**. LLM-as-judge alert
     triage. Shares only the word "eval"; no claim overlap with suite
     construction.
  6. `docs-promptfoo-classifier-grading.md` — **dismissed**. Grader
     implementation detail (`apiEndpoint`, gated HF repos, threshold
     recalibration per label set). No matrix or composition content.
  7. `docs-promptfoo-javascript-assertions.md` — **dismissed** as a candidate,
     but it supplies the useful prior that a bare-`type` assertion's
     *unspecified* parameters resolve to vendor defaults — the same shape as
     Claim 9's undocumented `0.75`. Not cited, because the parallel is
     structural and that note's claims are about a different assertion type;
     the guide can make the general rule once, from this note's concrete
     instance.
  8. `docs-promptfoo-llm-rubric.md` — **dismissed**. Audio-grading contract and
     judge-model selection. However, `llm-rubric` *is* the assertion type the
     vendor's array-form sibling config is forced into (Claim 6), which is a
     genuine and useful contrast — but the contrast is about cost per cell, not
     about that note's claims, so it is made against the config artifact in
     Concrete Artifacts rather than by citing the rubric note.
  9. `docs-langfuse-mcp-server.md` — **dismissed**. Different vendor,
     docs-MCP plumbing. Nothing on eval results or suite composition.
  10. `docs-google-sre-eliminating-toil.md` — **dismissed**. Toil taxonomy and
     the 50% operational-work cap. No eval-artifact or suite-construction
     claim.
  Note on the candidate list's usefulness: all ten are assertion-type or
  cross-vendor notes, and **none** is a suite-construction note — which is
  itself the signal that this page's subject area was a genuine gap in the
  corpus rather than a duplicate. The lexical retriever matched on shared
  eval vocabulary (`threshold`, `assertion`, `test`), not on subject matter.
  Additional cross-references were found by searching `source-notes/` directly
  (`grep -ril scenario`, `grep -ril glob`) and each verified per MINER.md §4b by
  re-reading the cited note and confirming the claim number:
  `docs-promptfoo-configuration-outputs.md` Claim 2 (Corroborates),
  `docs-promptfoo-configuration-huggingface-datasets.md` Claims 4 and 5
  (Corroborates), `docs-promptfoo-similar-assertion.md` Claims 1, 2, and 9
  (Corroborates), `docs-promptfoo-modular-configs.md` Claims 1, 2, and 9
  (Extends), `docs-promptfoo-configuration-caching.md` Claims 1 and 4 (Extends),
  `docs-promptfoo-configuration-rate-limits.md` Claims 3 and 12 (Extends),
  `docs-promptfoo-chat-threads.md` Claim 5 (Extends), plus
  `source-notes/docs-promptfoo-dataset-generation.md` and
  `source-notes/docs-promptfoo-configuration-rate-limits.md` as related-by-scope
  notes named in the Prospector's comments (read and confirmed non-overlapping
  for citation purposes; not cited by claim number because no specific claim
  was needed).
- **Quote discipline.** Every quoted passage was taken verbatim from the
  markdown source of the docs page or from the raw GitHub files fetched in this
  session. Non-adjacent sentences are quoted as separate `Quote` entries with
  their source attributed, never spliced into one string. Claims whose meaning
  is our synthesis across multiple source passages (notably Claims 3, 5, 6, 7,
  and 10) keep the synthesis in **Our assessment** and the `Quote` field
  carries only the source's own contiguous words. Code blocks are reproduced
  exactly as stored, including promptfoo's own YAML comments. The two code
  excerpts in Claim 9 and the Concrete Artifacts are verbatim from
  `promptfoo/promptfoo` @ `main` on 2026-10-03.
- `confidence_overall` is `emerging`: the config grammar — schema, expansion
  rule, `file://` syntax, glob forms, directory layout — is authoritative and
  individually **settled** (Claims 1, 2, 3, 6, 7). What is not settled is
  everything the page is silent about: cost and runtime (Claim 10), output
  naming (Claim 2), and failure behavior (Claim 8), which required reading the
  implementation because the docs do not state it. There are **no** measured
  runtimes, no cost figures, no pass rates, no failure reports, and no
  independent validation of the matrix pattern anywhere on the page or in the
  example repository. One claim is explicitly settled-by-code against silent
  docs (Claim 9's `0.75`) and one is marked emerging in its consequence half
  while settled in its mechanical half (Claim 8).