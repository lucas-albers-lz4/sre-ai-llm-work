---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/
source_type: docs
title: "Promptfoo Deterministic Metrics for LLM Output Validation"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-12
date_extracted: 2026-09-12
last_checked: 2026-09-12
status: current
confidence_overall: emerging
issue: "#1289"
---

# Promptfoo Deterministic Metrics for LLM Output Validation

> The vendor's reference catalog for the deterministic (no-judge) assertion
> tier of an LLM eval gate — the per-type config semantics, the
> deterministic-vs-model-graded boundary promptfoo draws itself, the
> silent-failure footguns (numeric coercion, cached cost, `tool-args-match`
> default-stripping), the fail-closed behaviors (`is-xml` DTD rejection,
> `tool-call-f1` malformed-output failure), and the trace/trajectory family
> that asserts directly over observability span data.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Deterministic
  metrics" reference page under `/docs/configuration/expected-outputs/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own assertion behavior — authoritative for what each assertion does
  with a given config, but vendor-positioned: the page reports no measured
  gate-failure-rate, drift, or cost figures, and there is no independent
  practitioner validation. Every clause below is directly checkable against an
  installed CLI.
- **Scope**: A reference catalog of the deterministic assertion types —
  string/structure checks (`contains*`, `equals`, `regex`, `starts-with`,
  `word-count`, `levenshtein`), schema/format checks (`is-json` /
  `contains-json` with JSON Schema, `contains-sql` / `is-sql` with authority
  allowlists, `is-xml` / `contains-xml`, `is-html` / `contains-html`), budget
  and metadata checks (`cost`, `latency`, `perplexity`, `finish-reason`,
  `is-refusal`), text-overlap metrics (`rouge-n`, `bleu`, `gleu`, `meteor`),
  `assert-set` grouping, extension hooks (`javascript`, `python`, `webhook`),
  and the trace/trajectory family (`trace-span-*`, `trajectory:*`, `skill-used`,
  `tool-call-f1`, `is-valid-*-call`). It does NOT cover the model-assistant
  types (sibling page #1288 / `classifier`, `similar`, `pi`, `select-best`)
  beyond naming them as the non-deterministic boundary. Code examples in the
  page arrive as collapsed single lines after HTML extraction; line breaks
  were restored at YAML boundaries with no wording changes.
- **Last updated**: Sep 12, 2026 by renovate[bot]; the page is undated but the
  documented examples describe the current `gpt-5` era.

## Extracted Claims

### Claim 1: Promptfoo itself draws the deterministic/model-graded line — `classifier`, `pi`, `select-best`, and `similar` are listed separately as checks that "use an additional model or external inference service"
- **Evidence**: A separate mini-table immediately after the main assertion
  table, with the excluded types and their requirements; the four rows name a
  HuggingFace classifier, a Pi Labs scorer, a grading model, and an embedding
  model respectively.
- **Confidence**: settled (documented product behavior)
- **Quote**: "These checks use an additional model or external inference service. Their sections remain here for existing links:" — with the requirement column reading "A HuggingFace classifier", "A Pi Labs scorer", "A grading model to compare outputs", and "An embedding model" for `classifier`, `pi`, `select-best`, `similar`.
- **Our assessment**: This is the vendor's own enumerated boundary, directly
  usable in the guide as the concrete answer to "what can be gated without a
  judge." The four excluded types are precisely the ones that inherit every
  judge-variance problem documented in `blog-promptfoo-asr-not-portable-metric.md`
  (#261). Novel vs the parent hub-page note (#1287 Claim 10), which states the
  two-family split in prose; this page enumerates the excluded set.

### Claim 2: "Deterministic" in promptfoo's sense means *no model judge*, not *no external dependency* — configured scripts, webhooks, and grouped assertions may still depend on external services
- **Evidence**: The page's opening sentence, immediately under the page title.
- **Confidence**: settled (documented product behavior; the caveat is the
  vendor's own framing of the catalog)
- **Quote**: "These assertions can check LLM output or provider metadata directly. Configured scripts, webhooks, and grouped assertions may still depend on external services."
- **Our assessment**: The guide-critical distinction for CI flake analysis.
  A `webhook` or `javascript` assertion with an external fetch is "deterministic"
  by promptfoo's taxonomy yet non-hermetic under Ch05's hermeticity rule
  (`guide/05-llm-ops-reliability.md:158-182`). The rule to extract: the
  deterministic tier is judge-free, but hermetically replayable only when the
  configured function/webhook makes no external calls — teams must audit the
  hooks, not just the type name, before treating a gate as hermetic.

### Claim 3: Every assertion type can be negated with a `not-` prefix (`not-equals`, `not-regex`), making absence assertions a first-class surface
- **Evidence**: The "tip" block above the assertion-type section, plus
  `not-`-prefixed examples throughout the page (e.g., `not-contains`,
  `not-is-xml`, `not-is-refusal`, `not-skill-used`, `not-tool-call-f1`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "Every test type can be negated by prepending `not-`. For example, `not-equals` or `not-regex`."
- **Our assessment**: Negation is how a gate asserts *absence* — e.g.,
  `not-skill-used` to fail a run that routed through a forbidden skill, or
  `not-contains:error` inside a grouped gate. The useful property for gates:
  negation doubles the expressible vocabulary at zero extra cost, and the
  fail-closed behaviors of the underlying type (Claims 8, 10) carry through to
  the negated form.

### Claim 4: `assert-set` groups assertions under a configurable pass threshold — "N of M structured checks green" gating expressed declaratively, mixable with model-graded checks
- **Evidence**: The "Assert-Set" section: the grouping / success-criteria
  framing, the `threshold: 0.5` example mixing `contains`, `llm-rubric`,
  `not-contains`, and `is-json`, and the weighted `threshold: 0.25` /
  `weight: 2.0` / `metric` variant.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `assert-set` groups multiple assertions together with configurable success criteria. This is useful when you want to apply multiple checks but don't need all of them to pass." and "threshold: 0.5 # 50% of assertions must pass"
- **Our assessment**: This is the CI-gating primitive the triage flagged: a
  group of checks with its own pass ratio, so "most of a suite must be green"
  is config rather than all-or-nothing. Two caveats for the guide: (a) the
  group is only as deterministic as its members — mixing in `llm-rubric` or
  `similar` (Claim 1) quietly reintroduces a judge into a "deterministic" gate;
  (b) per the parent page (#1287 Claim 3/5), `threshold: 0` on a set makes it
  pass always — the same can-it-fail? trap as at test-case level.

### Claim 5: `contains`/`icontains` coerce numbers to strings, so `value: 0` matches any output containing `0` — a literal-match integer footgun; the CSV/XLSX/Sheets compact form needs quoting for values containing commas
- **Evidence**: The "Contains" section's conversion sentence, and the
  "Contains-Any" section's compact-form warning.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Both assertions accept string or number values. Numbers are converted to strings, so `value: 0` matches output containing `0`." and "Compact assertion strings in CSV, XLSX, and Google Sheets `__expected` columns use comma-separated values. Quote values containing commas; see [CSV test cases](/docs/configuration/test-cases/#csv-with-assertions) for escaping details."
- **Our assessment**: Two silent test-correctness hazards. The coercion
  behavior means `value: 0` is satisfied by `10`, `200`, `0.5`, `build-2049` —
  there is no integer-equality check on the substring family; an exact
  numeric gate belongs on `equals` with the string form of the literal.
  The CSV quoting issue is a fixture-authoring trap: an unquoted `1,000` is
  parsed as two values. Both belong in a "deterministic gates can still lie"
  footnote for Ch05's eval methodology.

### Claim 6: The `cost` assertion can only gate provider-reported cost — an "unknown cost cannot be checked," and response-cache cost reporting means fresh-cost gating requires `--no-cache`
- **Evidence**: The "Cost" section's requirement sentence and its CLI caveat,
  beside an example asserting two OpenAI providers under a $0.001 threshold.
- **Confidence**: settled (documented product behavior)
- **Quote**: "This requires the provider to return cost information; an unknown cost cannot be checked. Use `--no-cache` when comparing fresh inference costs, because response-cache cost reporting depends on the provider."
- **Our assessment**: A budget gate that reads cached cost is measuring the
  wrong thing — cost for a cache hit is the replayed response's cost, not a
  fresh inference. This is the deterministic-tier twin of `docs-promptfoo-configuration-caching.md`
  (#1275) Claim 8 (`--no-cache` + `--repeat` required for fresh runs): budget
  gates must opt out of the default 14-day eval cache or the "cost < $0.001"
  number is not what it appears. Also note the asymmetry: cost is only as
  reliable as the provider reporting it — an eval gate on a provider that
  doesn't return cost cannot be audited, so a "cost gate" on such a provider
  is silently no gate at all.

### Claim 7: JSON assertions optionally validate against a JSON Schema, and a schema can be imported from a file — `is-json` validates the whole output, `contains-json` the embedded JSON, with `file://` keeping schemas version-controlled beside the config
- **Evidence**: The "Is-JSON" and "Contains-JSON" sections: the optional
  `value` schema (inline YAML or raw JSON) and the file-import form.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You may optionally set a `value` as a JSON schema in order to validate the JSON contents:" and "If your JSON schema is large, import it from a file:" and "If your JSON schema is large, import it from a file: / `value: file://./path/to/schema.json`"
- **Our assessment**: Schema-from-file is the pattern an operator wants: the
  schema lives in the repo, is reviewed like code, and pins the output shape a
  migration must keep. The whole-output (`is-json`) vs embedded (`contains-json`)
  distinction resolves which gate to use when output carries prose around
  structured data — asserting `is-json` on an output that wraps its JSON in
  text fails correctly, so the type choice itself is a spec decision.

### Claim 8: `is-xml` fails closed — it rejects documents with a DTD internal subset (unvalidatable entity replacement) and loads no external resources during validation, and it requires the whole output to be well-formed XML
- **Evidence**: The "Is-XML" how-it-works bullet list, the DTD paragraph, and
  the failure examples (plain text, mixed content, XML documents under `is-html`).
- **Confidence**: settled (documented product behavior)
- **Quote**: "`is-xml` rejects documents with a DTD internal subset because Promptfoo cannot safely validate the subset's declarations and entity replacement text. External resources are not loaded during validation." and "The `is-xml` assertion requires the entire output to be a supported well-formed XML document."
- **Our assessment**: The DTD rejection and no-external-resources rule are the
  security-relevant details: a tool that validated against external entity
  references would open an XXE-shaped surface in the eval harness itself.
  Failing closed here (no partial validation) is the right default for a CI
  gate — an XML block the harness can't fully validate is reported as failure,
  not silently accepted. `not-is-xml`'s scope ("XML outside Promptfoo's
  supported subset" also passes the negation) is a subtlety to note when
  asserting absence of XML.

### Claim 9: `is-sql` validates that output is a non-empty valid SQL statement, treating `SELECT a b FROM t` as a likely missing comma rather than implicit aliasing, and supports an optional database-type plus table/column authority allowlist
- **Evidence**: The "Is-SQL" section: the missing-comma statement, the
  `node-sql-parser` installation requirement, the `databaseType` list
  (MySQL default; Athena, BigQuery, DB2, FlinkSQL, Hive, MariaDB, Noql,
  PostgresQL, Redshift, Snowflake(alpha), Sqlite, TransactSQL), and the
  `allowedTables`/`allowedColumns` authority format `{type}::{dbName}::{tableName}`
  / `{type}::{tableName}::{columnName}`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `is-sql` assertion checks if the LLM output is a non-empty valid SQL statement. For simple column lists, it treats `SELECT a b FROM t` as a likely missing comma rather than implicit aliasing." and "The format of allowedTables: `{type}::{dbName}::{tableName} // type could be select, update, delete or insert`"
- **Our assessment**: The authority allowlist is the policy hook: an
  operator can forbid generated SQL from touching tables it must not reference
  (`select::null::departments`) with a regex-shaped allowlist. Note the force
  needed to use it — `is-sql` pulls a parser dependency (`node-sql-parser`)
  that must be installed in the eval environment, and the allowlist condition
  is checked *in addition to* syntax validity, so a syntactically-valid query
  against a non-allowlisted table fails. That makes `is-sql` the strongest
  example on the page of a deterministic assertion carrying real policy.

### Claim 10: `tool-call-f1` fails closed on malformed output — when parsing work exceeds limits or JSON delimiters are unmatched, the assertion fails with an explanation instead of reporting a partial F1 — and it scores unordered tool-name sets only
- **Evidence**: The "tool-call-f1" section: the recovery/limit statements, the
  unordered-comparison note, and the scored pass/fail table.
- **Confidence**: settled (documented product behavior)
- **Quote**: "If malformed output exceeds limits on parsing work or unmatched JSON delimiters, the assertion fails with an explanation instead of reporting a partial F1 score. This failure also applies to `not-tool-call-f1`." and "This uses **unordered set comparison** — only the presence of tool names matters, not the order or frequency of calls."
- **Our assessment**: Two design choices worth extracting. First, fail-closed
  on malformed output (including under negation) means an agent that emits
  garbage JSON cannot "pass" on a forgiving partial score — the gate refuses
  to grade ungradeable output, which is the correct evasion posture. Second,
  names-only set comparison is both a strength (order/frequency-insensitive,
  robust to agentic variance) and a limit (arguments are not validated here —
  pairs with `trajectory:tool-args-match`, Claim 11, for full call checking).
  With `threshold` defaulting to 1.0, a partial tool-selection is a failure
  unless a team deliberately lowers it.

### Claim 11: `trajectory:tool-args-match` strips declared `defaults` before matching, so listing the same key in both `args` and `defaults` makes an otherwise-matching call fail — a documented config footgun with explicit pass/fail tables
- **Evidence**: The "Tolerating default arguments" section: the
  stripping-before-matching rule and the observed-arguments outcome table.
- **Confidence**: settled (documented product behavior, with worked pass/fail rows)
- **Quote**: "Stripping runs before matching in both modes, but `partial` mode already ignores extra arguments, so `defaults` is only meaningful with `mode: exact`. Keep a key in `args` *or* `defaults`, not both: an observed value equal to its default is stripped before the `args` comparison runs, so listing the same key in both can make an otherwise-matching call fail."
- **Our assessment**: A concrete, counter-intuitive silent-failure mode in the
  highest-signal assertion family for agent evals. The surrounding table shows
  the intended use: `defaults` tolerates harmless optional arguments (e.g. `page:
  1`, `page_size: 5`) while `mode: exact` still rejects hallucinated extras
  (`delete_database: true`) — the exact/`ignore` pairing is the tolerance
  toolkit for agent argument verification. Worth a "documented footguns" entry
  in Ch03's agent-evaluation material, alongside the fail-closed cases.

### Claim 12: The trace/trajectory assertion family requires trace data — the assertions throw an error when traces are unavailable rather than failing, so an eval suite built on them has an explicit observability dependency that is itself an operational risk
- **Evidence**: The trajectory note, the trace-section notes, and the
  explicit error-vs-fail statement for `trace-span-count`.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Trajectory assertions require trace data. Enable tracing for the eval and use a provider that emits tool-oriented spans or attributes." and "If trace data is not available, the assertion will throw an error rather than failing, indicating that the assertion could not be evaluated."
- **Our assessment**: This is the trade worth naming: the same surface that
  makes evals and observability share a schema (asserting over the span data
  Ch02 instruments) also couples the gate's health to the tracing pipeline.
  If tracing is disabled or the provider stops emitting tool-oriented spans,
  the gate fails loud (good — no silent skip), but the run is now red for an
  infrastructure reason, not a model reason. A trace-coupled gate needs the
  tracing dependency itself monitored, and the span-naming contract the
  producer side must honor to make the assertions match anything
  (`blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claims 2/12).

### Claim 13: `trace-error-spans` detects errors automatically across status codes (≥400), error attributes, and OTel status conventions — with `max_count` and `max_percentage` error-rate limits
- **Evidence**: The "Trace-Error-Spans" section's detection-method list and
  the four configuration examples (no errors; ≤2; ≤5% rate; API-only).
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `trace-error-spans` assertion detects error spans in a trace and ensures the error rate is within acceptable limits." and "**Status codes**: HTTP status codes >= 400" and "**Error attributes**: Checks for `error`, `exception`, `failed`, `failure` attributes" and "**OpenTelemetry standards**: `otel.status_code: ERROR`, `status.code: ERROR`" and "**Status messages**: Messages containing \"error\", \"failed\", \"exception\", \"timeout\", \"abort\""
- **Our assessment**: The auto-detection list is the contract: the assertion
  infers "error" from four independent signals, so a span that is an error but
  fails to set any of them escapes the check. That makes the guidance
  attributing spans per the Honeycomb note (set `error.type`, propagate error
  status — its Claim 9) the producer-side half of making this gate accurate.
  `max_percentage` is the error-budget-in-config primitive — a release gate
  "≤5% error rate on API spans" is expressed declaratively here.

### Claim 14: Budget/precondition gates carry hidden requirements — `latency` requires `--no-cache` to be measuring the target call at all, and `perplexity`/`perplexity-score` require provider `logprobs` support that only recent OpenAI GPT/Azure APIs provide
- **Evidence**: The "Latency" note and the "Perplexity" warning block.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Note that `latency` requires that the [cache is disabled](/docs/configuration/caching/) with `promptfoo eval --no-cache` or an equivalent option." and "Perplexity requires the LLM API to output `logprobs`. Currently only more recent versions of OpenAI GPT and Azure OpenAI GPT APIs support this."
- **Our assessment**: Same cache coupling as Claim 6 but sharper: a `latency`
  gate on a warm cache measures replay, not the model. `perplexity` is the
  most constrained gate on the page — on a provider without `logprobs` it is
  unavailable, and the page itself warns that cross-model perplexity
  comparisons "may not be meaningful" unless tokenization/vocabulary roughly
  match, so a perplexity gate is model-scope-local, not a portable threshold.

### Claim 15: F-score is not an assertion type on this page — it is a derived metric built from named JavaScript assertions over `derivedMetrics`, a categorization the page states explicitly
- **Evidence**: The callout directly under the main assertion table, and the
  "F-Score" section's construction from named `javascript` assertions +
  `derivedMetrics` formulas.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The [F-score](#f-score) section describes a derived metric built from named JavaScript assertions, not an assertion type."
- **Our assessment**: Included mostly to prevent misreading the catalog: a
  reviewer scanning the table will otherwise count F-score as an assertion
  type, when it is actually the aggregation example the parent page
  (`docs-promptfoo-assertions-metrics.md` #1287) covers in depth — its
  `derivedMetrics` F1 artifacts. It also embodies the deterministic-vs-judge
  point in miniature: the base classification signals are collected by
  deterministic `javascript` assertions (`weight: 0` metric carriers) and the
  composite is arithmetic, so the derived F-score is hermetic — unlike a
  model-graded aggregate.

## Concrete Artifacts

### assert-set threshold gate (verbatim from "Assert-Set"; deterministic + model-graded mix)

```yaml
tests:
  - assert:
      - type: assert-set
        threshold: 0.5 # 50% of assertions must pass
        assert:
          - type: contains
            value: hello
          - type: llm-rubric
            value: is a friendly response
          - type: not-contains
            value: error
          - type: is-json
```

Weighted variant:

```yaml
assert:
  - type: assert-set
    threshold: 0.25 # 1 out of 4 equal weight assertions need to pass
    weight: 2.0 # This set is weighted more heavily in the overall score
    metric: quality_checks
    assert:
      - type: similar
        value: expected output
      - type: contains
        value: key phrase
```

### Cost gate (verbatim from "Cost")

```yaml
providers:
  - openai:gpt-5-mini
  - openai:gpt-5
assert:
  # Pass if the LLM call costs less than $0.001
  - type: cost
    threshold: 0.001
```

### Schema-from-file JSON gate (verbatim from "Is-JSON" / "Contains-JSON")

```yaml
assert:
  - type: is-json
    value: file://./path/to/schema.json
```

### SQL authority allowlist (verbatim from "Is-SQL")

```yaml
assert:
  - type: is-sql
    value:
      databaseType: 'MySQL'
      allowedTables:
        - '(select|update|insert|delete)::null::departments'
      allowedColumns:
        - 'select::null::name'
        - 'update::null::id'
```

### `trajectory:tool-args-match` defaults tolerance (verbatim from the section of that name)

```yaml
tests:
  - assert:
      - type: trajectory:tool-args-match
        value:
          name: orders
          mode: exact
          args:
            status: Q
          defaults:
            page: 1
            page_size: 5
```

Documented outcomes (verbatim rows):

| Observed tool arguments | Outcome | Reason |
| --- | --- | --- |
| `{ status: 'Q' }` | pass | matches expected exactly |
| `{ status: 'Q', page: 1 }` | pass | `page: 1` equals the declared default, stripped before matching |
| `{ status: 'Q', page: 1, page_size: 5 }` | pass | both defaults stripped |
| `{ status: 'Q', page: 2 }` | fail | `page: 2` does not equal the declared default (1), so it stays in the payload; `exact` mode then rejects the unexpected extra |
| `{ status: 'Q', delete_database: true }` | fail | `delete_database` is not in `args` or `defaults` |

### Trace-error-spans error-budget gate (verbatim from "Trace-Error-Spans")

```yaml
assert:
  # No errors allowed
  - type: trace-error-spans
    value: 0 # Backward compatible - simple number means max_count
  # Allow at most 2 errors
  - type: trace-error-spans
    value:
      max_count: 2
  # Allow up to 5% error rate
  - type: trace-error-spans
    value:
      max_percentage: 5
  # Check errors only in API calls
  - type: trace-error-spans
    value:
      pattern: '*api*'
      max_count: 0
```

### Batched-vs-sequential tool-call assertion (verbatim from "Asserting batched vs sequential tool calls")

```yaml
tests:
  - assert:
      - type: trajectory:tool-sequence
        value:
          mode: exact
          steps:
            - search_orders
            - search_orders
      - type: javascript
        value: |
          // Both tool calls must have been emitted by the same LLM generation.
          const turns = context.trace.spans
            .filter((s) => s.attributes['tool.name'] && s.attributes['gen_ai.turn.index'] != null)
            .map((s) => s.attributes['gen_ai.turn.index']);
          return turns.length >= 2 && new Set(turns).size === 1;
```

With the page's reasoning attached: "Prefer this over counting total `gen_ai.turn`
spans: a tool-using task normally takes at least two generations (one to emit the
tool calls, one to fold the results into the answer), so `trace-span-count ... max: 1`
would reject a correctly-batched run."

Source for all artifacts: https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/ — sections as noted. All copied character-for-character from the rendered page (code blocks re-flowed only at the newline level to restore line breaks lost in HTML extraction).

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 10** (the
    deterministic family vs the model-assisted family split) and **Claim 11**
    (the trace/trajectory assertion family listing) — this page supplies the
    per-type semantics and the enumerated excluded set underneath those
    hub-page claims. This note is the config-level deep-dive the Prospector
    asked for; no re-extraction of the bare name list. (Verified: #1287
    Claims 10, 11.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 5** (`assert-set`
    grouping with its own `threshold`, "The same applies to an `assert-set`
    threshold.") — corroborates this note's Claim 4 from the scoring-side
    parent page: the set mechanics (weights, threshold semantics) are defined
    on the hub page, the worked CI-gate example here. (Verified: #1287 Claim 5.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8**
    (`--no-cache` + `--repeat` is the only way to make every run fresh;
    per-repeat cache namespaces) — the mechanism behind this note's Claims 6
    and 14: cost and latency gates both require opting out of the default
    cache, or they measure replay. (Verified: #1275 Claim 8.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 8** (two
    judges with identical 80% accuracy can show a 14-point gap from differing
    TPR/FPR) — the existence proof for *why* the deterministic tier matters:
    judge-graded checks are the non-portable layer (this note's Claim 1
    boundary), while deterministic assertions replay identically across model
    upgrades. (Verified: #261 Claim 8.)
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claim 2** (three mandatory span attributes) and **Claim 12** (the strict
    `<operation> <target>` span-naming pattern) — the producer-side contract
    that this note's trace/trajectory family (Claims 11-13) consumes as its
    input; `trajectory:tool-used` can only match spans named and attributed the
    way the Honeycomb note prescribes. (Verified: #2 Claims 2, 12.)
  - `source-notes/docs-langfuse-evaluation-core-concepts.md` **Claim 4** (the
    five-method taxonomy, with "Code evaluators" as a first-class method with a
    defined "use when" condition) — a second vendor independently placing
    programmatic (deterministic) checks alongside LLM-as-a-judge in its eval
    taxonomy, corroborating that the deterministic tier is a universal eval
    primitive, not promptfoo-specific. (Verified: #195 Claim 4.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** (pre-deployment
    red teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule) — corroborates the CI-gate framing this note's threshold-bearing
    gates (Claims 4, 6, 13, 14) operationalize. (Verified: #555 Claim 4.)

- **Contradicts**: None identified. This is a first-party vendor reference
  catalog; it opposes no existing source-note claim. Checked `CONTRADICTIONS.md`
  (the only entry is #1150, an unrelated LiteLLM-routing contradiction) and open
  `contradiction`-labeled issues. The closest surface is a nuance, not a
  conflict: `blog-promptfoo-asr-not-portable-metric.md` (#261) frames *all*
  promptfoo assertion types through measurement-validity risk, while this page
  shows a large tier with no judge in the loop — these are complementary, not
  opposing (deterministic checks are precisely the portable kind #261
  recommends); #261's judge-bias claims apply to this page's excluded set
  (Claim 1), which #261 never addresses.

- **Extends**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) — carries the
    hub page's catalogue claims down to per-type config semantics, documented
    failure modes, and the operational preconditions (cache, logprobs, parser
    dependency, trace data) the parent page does not detail.
  - `source-notes/docs-promptfoo-configuration-caching.md` (#1275) — extends
    the "a green gate may evidence nothing" thesis from the cache layer to the
    deterministic-assertion layer: cached cost (Claim 6), cached latency
    (Claim 14), and the numeric-coercion/`defaults` misconfigurations (Claims
    5, 11) are three more ways a deterministic gate reports green while
    verifying the wrong thing.
  - `source-notes/docs-promptfoo-dataset-generation.md` **Claim 5** (generated
    test cases are non-deterministic by construction, with no pinning/seed
    story) — the complementary half of the determinism story this page
    documents: the assertions are deterministic, but if they run over
    synthesized, unpinned fixtures, the *dataset* is still non-replayable.
    A gate is only hermetic when both halves hold. (Verified: #1277 Claim 5.)
  - `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`
    **Claim 9** (setting `error.type` and propagating error status turns
    failures into first-class navigation primitives) — the producer-side
    practice that makes this page's `trace-error-spans` auto-detection
    (Claim 13) actually see the errors it checks for. (Verified: #2 Claim 9.)

- **Novel**: First corpus coverage of the **per-type deterministic-assertion
  semantics** — the two sibling promptfoo config notes (#1275 cache, #1277
  datasets) and the hub page (#1287) cover the aggregation model and the
  catalogue split but carry none of these specifics. Specifically new:
  1. **The vendor-drawn deterministic/model-graded boundary** as an enumerated
     set (Claim 1) — four named exceptions, directly citable by Ch05/Ch06.
  2. **The "deterministic ≠ hermetic" caveat** (Claim 2) — scripts/webhooks
     still touch external services; the Ch05 hermeticity-replayability
     distinction made explicit in a vendor catalog.
  3. **Silent-failure footguns**: numeric coercion making `value: 0` match any
     output containing `0` (Claim 5); the CSV comma-quoting hazard (Claim 5);
     the `tool-args-match` `args`+`defaults` double-listing failure with its
     pass/fail table (Claim 11).
  4. **Fail-closed behaviors**: `tool-call-f1` refusing to score malformed
     output (Claim 10); `is-xml` rejecting DTD internal subsets and loading no
     external resources (Claim 8).
  5. **Operational preconditions**: cost requiring provider-reported figures
     plus `--no-cache` (Claim 6); latency requiring `--no-cache` (Claim 14);
     perplexity requiring provider `logprobs` with a cross-model
     comparability warning (Claim 14); trace assertions throwing when traces
     are absent (Claim 12).
  6. **Policy-in-config deterministic gates**: `is-sql` table/column authority
     allowlists (Claim 9) and `trace-error-spans` `max_percentage` error-budget
     gating (Claim 13) — the strongest examples of deterministic assertions
     carrying real release policy.

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — §Evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md:261`)**:
  - At **"Metrics without a unit are noise"**, add the deterministic tier as
    the portable-measurement layer: deterministic assertions are the check
    family that *survives* model/provider changes (no judge in the loop,
    Claim 1 boundary, corroborated by #261's judge-portability argument),
    while the excluded set (`classifier`/`pi`/`select-best`/`similar`) inherits
    judge variance. Give the "use deterministic checks for the always-on tier,
    judge-graded checks for the calibration/periodic tier" split.
  - In the valut/gate-checklist family (this page is the config-level twin of
    #1287's "can your gate actually fail?" items), add the deterministic-tier
    traps: audit `cost`/`latency` gates for the eval cache (`--no-cache`
    required, Claims 6/14, extending #1275 Claim 8); spell out numeric-coercion
    and CSV-compact hazards (Claim 5); flag `assert-set` gates that mix in
    model-graded members as non-hermetic despite the "deterministic" type name
    (Claims 2/4); note that `is-sql` carries a parser dependency and `perplexity`
    a provider-`logprobs` dependency (Claims 9/14) so "deterministic" does not
    mean dependency-free.
  - The hermeticity material at `guide/05-llm-ops-reliability.md:158-182` can
    cite Claim 2's vendor-owned phrasing that scripts/webhooks/groups may still
    depend on external services — the page's own acknowledgment that its
    deterministic tier is judge-free but not automatically hermetic.
- **Chapter 02 (Observability) — trace-based assertions / eval-input provenance**:
  Add the trace/trajectory assertion family (Claims 11-13) as the
  consumer-side contract on the schema Ch02 instruments: the eval gate and the
  observability pipeline share one span schema (span naming/attribution per
  #2 Claims 2/12), and a trace-coupled gate throws rather than failing when
  traces are absent (Claim 12) — so the tracing dependency is now part of the
  eval gate's own availability, and the gate needs the tracing pipeline
  monitored with it. `trace-error-spans` auto-detection (Claim 13) is exactly
  as accurate as the spans' error attribution (#2 Claim 9).
- **Chapter 03 (Runbooks and Agents) — agent evaluation**: Add the
  trajectory/tool-call assertion toolkit as the agent-route verification
  surface: `trajectory:tool-used` / `:tool-sequence` / `:step-count` /
  `skill-used` for "did the right skill/tool route happen"; `tool-args-match`
  with the `defaults`/`ignore` tolerance patterns for argument verification
  (Claim 11, Concrete Artifacts table); `tool-call-f1` for unordered tool-set
  scoring with a deliberate `threshold` (Claim 10); and `assert-set` for "N of
  M agent checks green" release gating (Claim 4). Document the `args`+`defaults`
  double-listing footgun (Claim 11) as a known config trap.
- **Chapter 06 (Security and Trust) — red-teaming as a CI gate**: Use the
  deterministic vs model-graded boundary (Claim 1) as the cost tiering for
  red-team gates: deterministic string/schema/policy checks (`is-sql` allowlists
  Claim 9, `not-skill-used` absence checks Claim 3, `is-refusal` guardrail
  checks) form the cheap always-on layer; the model-jugged sweeps sit on top.
  Include the fail-closed properties (Claims 8, 10) as the reason malformed or
  unvalidatable adversarial output does not slip a deterministic gate.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/deterministic/).
  The page is a self-contained reference catalog; the sibling sub-pages it
  links to (`javascript/`, `python/`, `similar/`, `classifier/`, `is-json`↔
  etc.) are either their own extraction issues (#1288 classifier is the
  model-judge sibling) or separate reference pages without additional
  deterministic-gate semantics, so no sub-pages were followed — per the
  Prospector's guidance, the design signal (boundary, footguns, preconditions,
  fail-closed behavior) was extracted rather than the whole name table.
- **Dedupe handled per Prospector**: the parent index page
  (`docs/configuration/expected-outputs/`) was extracted under issue #1287 as
  `docs-promptfoo-assertions-metrics.md`; this note deliberately does NOT
  re-extract the bare type-name list or the aggregation/scoring semantics, and
  only references #1287's claims for cross-checking. Sibling #1288 (classifier)
  is the model-judge half of the same boundary and is left to its own
  extraction; no overlap was extracted here.
- Quotes were verified character-for-character against the fetched rendered
  content before writing; code blocks arrive as single lines after HTML
  extraction, so line breaks were restored at YAML boundaries only (no wording
  changes), consistent with the sibling #1275 note's convention. Table rows
  (the `trajectory:tool-args-match` outcome table, the error-detection bullets)
  copied verbatim.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1275, #1277, #1287): individual mechanism/default claims (Claims 1-15)
  are settled-for-product-behavior and directly checkable against an installed
  CLI, but this is vendor documentation with no measured failure-rate, drift,
  or cost figures and no independent practitioner validation — the
  operational-consequence framing (cache coupling of budget gates, trace
  dependency risk, fail-closed posture) is the Miner's synthesis on top of
  documented behavior.
- `date_published` uses the page's "Last updated Sep 12, 2026" date (undated page).
- **Candidate dismissal** (from `miner-related-notes.md`, read before
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `blog-promptfoo-owasp-red-teaming.md` — red-team methodology/SDLC phases;
    **cited** (Corroborates, Claim 4) for the CI-gate theme, no assertion
    semantics overlap.
  - `docs-promptfoo-assertions-metrics.md` — the parent hub page (#1287);
    **cited heavily** (Corroborates/Extends, Claims 5/10/11) as the strongest
    cross-reference.
  - `blog-pagerduty-sre-agent-triage.md` — AI-incident triage by an SRE Agent;
    no deterministic-assertion surface; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-creating-production-launch-plan.md`,
    `docs-google-sre-reliable-product-launches.md` — Google SRE book/workbook;
    no LLM-eval content; dismissed.
  - `blog-promptfoo-red-team-gemini.md`, `blog-promptfoo-red-team-claude.md` —
    per-model red-team plugin config; use a latency/threshold assert as a tool
    but carry no deterministic-assertion semantics; dismissed.
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — agent spectrum/guardrail
    taxonomy; no assertion-gate content; dismissed.
  - The remaining cross-refs
    (`docs-promptfoo-configuration-caching.md`, `docs-promptfoo-dataset-generation.md`,
    `docs-langfuse-evaluation-core-concepts.md`, `blog-promptfoo-asr-not-portable-metric.md`,
    `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`) were found by
    searching `source-notes/`, per the Prospector's overlap list and MINER.md §4.
- No contradiction issue filed: verified against `CONTRADICTIONS.md` (only open
  entry is #1150, unrelated LiteLLM routing) and open `contradiction`-labeled
  issues. The closest surface — #261's measurement-validity framing applying
  to the excluded (model-graded) set only — is complementary, not opposing.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.