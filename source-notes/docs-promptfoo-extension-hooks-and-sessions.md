---
source_url: https://www.promptfoo.dev/docs/configuration/reference
source_type: docs
title: "Promptfoo Configuration: Reference — Extension Hooks, Session Management, and Run-Control Defaults"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-02
date_extracted: 2026-10-03
last_checked: 2026-10-03
status: current
confidence_overall: settled
issue: "#1559"
---

# Promptfoo Configuration: Reference — Extension Hooks, Sessions, and Run-Control Defaults

> The canonical promptfoo schema page, mined for its one un-owned surface: the
> four-stage JavaScript/Python **extension-hook** lifecycle — a shallow-merge
> contract that replaces nested objects rather than deep-merging them, a
> persistence rule (mutate *and* return, except `afterAll`, whose return is
> discarded), and verdict fields (`success`, `score`, `response.output`) that
> are structurally un-overridable — plus the documented `response.sessionId` >
> `vars.sessionId` precedence that can silently orphan a session, and the
> `filterSampleSeed` / `suggestionsCount` run-control defaults that decide
> whether two CI runs grade the same population.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo's canonical YAML/JSON
  configuration schema reference, "Evals > Configuration > Reference")
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (site banner: now part of OpenAI), page footer "Last updated on Oct 2, 2026
  by mldangelo-oai". First-party documentation of the tool's own schema and
  hook contract — authoritative for promptfoo product behavior, vendor-
  positioned, and unaccompanied by any measured evidence, test matrix, or
  version-history entry for the hook semantics. Every claim below is
  checkable against an installed CLI, and none of it is independently
  validated.
- **Scope**: This note covers only the page's residual surface that no prior
  note owns: the **Extension Hooks** section (available hooks and their
  context shapes, persistence rule, shallow-merge semantics, non-overridable
  verdict fields, calling conventions, registration), the **Session Management
  in Hooks** subsection (session-id precedence, `sessionParser`, iterative
  `sessionIds`), and the `filterSampleSeed` and `suggestionsCount`
  `commandLineOptions` rows plus the `ResultSuggestion` interface. It
  deliberately does **not** re-extract the transformation pipeline, the
  `Config`/`Test Case`/`Assertion` schema tables, `evaluateOptions.timeoutMs` /
  `maxEvalTimeMs`, `maxConcurrency` / `delay`, `basePath`, `env` / `envPath`,
  `cache`, `flaggedInput` / `flaggedOutput`, `storeOutputAs`, or the
  `filterErrorsOnly` / `filterFailing` / `filterFailingOnly` / `retryErrors`
  rows — all owned by sibling notes (see Cross-References and Extraction
  Notes).
- **Not covered**: the page's TypeScript interface dumps (`TestSuite`,
  `UnifiedConfig`, `ProviderResponse`, `EvaluateResult`, `GradingResult`, …)
  are schema listings with no defaults, semantics, or failure modes beyond the
  specific fields cited here, and were treated as reference, not claim
  material.

## Extracted Claims

### Claim 1: `extensions` is promptfoo's supported in-band code-execution surface — four lifecycle hooks (`beforeAll`, `afterAll`, `beforeEach`, `afterEach`) in JavaScript *or* Python, each receiving a **different** context shape, and each hook's context enumerates a disjoint, deliberately narrow set of mutable fields
- **Evidence**: The `extensions` row of the top-level `Config` table, the
  "Available Hooks" table (name / description / context columns), and the four
  per-hook property tables under "Extension Hooks" (`beforeAll`, `beforeEach`,
  `afterEach`, `afterAll`).
- **Confidence**: settled (documented product behavior; the hook names, file
  types, and context shapes are stated explicitly)
- **Quote**: "List of extension files to load. Each extension is a file path with a function name. Can be Python (.py) or JavaScript (.js) files. Supported hooks are 'beforeAll', 'afterAll', 'beforeEach', 'afterEach'."
- **Quote** (Available Hooks table, description column): "Runs before the entire test suite begins" / "Runs after the entire test suite has finished" / "Runs before each individual test" / "Runs after each individual test"
- **Quote** (Available Hooks table, context column, one cell per row): "`{ suite: TestSuite }`" / "`{ results: EvaluateResult[], prompts: CompletedPrompt[], suite: TestSuite, evalId: string, config: Partial<UnifiedConfig> }`" / "`{ test: TestCase }`" / "`{ test: TestCase, result: EvaluateResult }`"
- **Quote** (afterEach table, description cells): "Custom numeric metrics (e.g., `num_turns`, `cost_usd`)." / "Structured data (e.g., tool call details, URLs)." / "Response-level metadata (e.g., session viewer URLs)."
- **Our assessment**: Buy it as the framing claim — it establishes that
  promptfoo has a documented, vendor-blessed place to run arbitrary operator
  code *inside* the eval lifecycle, which is the surface where every other
  claim in this note becomes operationally load-bearing. The shapes are
  asymmetric in a way that matters: `beforeAll` gets the whole `suite` and can
  therefore append test cases and default assertions before anything runs;
  `beforeEach` gets only a `test`; `afterEach` gets a `test` plus a `result`
  and is the only per-test hook that sees the graded outcome; `afterAll` gets
  the completed run (`results`, `prompts`, `evalId`, the resolved `config`) and
  is explicitly not a mutation point (Claim 2). The narrow per-hook field
  tables are effectively a **capability grant list** — a hook cannot reach
  anything not listed for its stage, which is a real (if undocumented-as-such)
  safety property: there is no documented `afterEach` handle on the suite's
  other rows.

### Claim 2: The hook contract is return-value-based, and the four hooks are asymmetric — `beforeAll` / `beforeEach` / `afterEach` must **return** the mutated context for changes to persist, while `afterAll`'s return value is discarded and it is restricted to side effects and read-only operations
- **Evidence**: The closing paragraph of "Implementing Hooks" and the `afterAll`
  section's opening sentence. The vendor's own Python and JavaScript examples
  are consistent with the rule: `beforeAll` / `beforeEach` branches end in
  `return context`, while the `afterAll` branches only print.
- **Confidence**: settled (documented product behavior; the two statements and
  the examples agree)
- **Quote**: "The `beforeAll`, `beforeEach`, and `afterEach` hooks may mutate specific properties of their respective `context` arguments in order to modify evaluation state. To persist these changes, the hook must return the modified context."
- **Quote**: "The `afterAll` hook is intended for side effects (sending to monitoring, cleanup, etc.) and its return value is not persisted. Use it for read-only operations on the completed evaluation."
- **Our assessment**: Buy it — this is the lifecycle's core trap, and it is
  *silent*. In-process mutation without a return (the natural JS/Python
  reflex, and the only way to write it if you have read a `beforeEach` example
  that mutates in place) writes nothing to the eval: no error, no warning, and
  the run looks exactly like a hook that did nothing. The failure is only
  visible downstream — a `beforeEach` that fails to return leaves `vars` as
  written, so a test runs against un-sessioned state. Two things the page
  does **not** state, flagged as unverified and worth a note in the guide
  rather than an inference: (a) what happens if a hook **throws** — there is
  no documented error contract anywhere in the section, so unlike the
  `javascript` assertion (where a throw is a documented hard fail per
  `docs-promptfoo-javascript-assertions.md` Claim 2) an operator cannot assume
  hooks fail closed; (b) whether the returned object is merged *into* the
  original context or replaces it wholesale — see Claim 3, where the merge
  semantics are stated but the omitted-key behavior is not.

### Claim 3: The merge is explicitly **shallow** — returned properties replace existing values at the top level, and nested objects are "replaced entirely, not deep-merged", so a hook that returns `metadata` for enrichment silently discards every sibling key under `metadata`
- **Evidence**: The sentence immediately following the persistence rule in
  "Implementing Hooks" — the page's only statement of merge semantics, and the
  reason this page was flagged as an un-mined surface (zero corpus coverage
  of the merge rule before this note).
- **Confidence**: settled (documented product behavior; the page is explicit
  and gives a concrete nested example)
- **Quote**: "All merges are shallow: returned properties replace existing values at the top level. Nested objects (e.g., `metadata: { nested: { a: 1 } }`) are replaced entirely, not deep-merged."
- **Our assessment**: Buy it — this is the same "documented divergence between
  config appearance and behavior" class the corpus already tracks for
  test-case-level transform overrides (`docs-promptfoo-configuration-guide.md`
  Claim 2), and it is the more dangerous instance because it lives on the
  metadata path that every reporting hook depends on. Concretely: a `beforeAll`
  hook that wants to stamp `metadata: { suite_env: 'canary' }` onto the suite
  will *replace* the whole `metadata` object rather than add a key to it, so
  any metadata promptfoo or a teammate put there is gone, and the run does not
  complain. The page's own worked session example demonstrates the correct
  defensive shape (`vars: { ...context.test.vars, sessionId }` — spread first,
  then override), which is the only evidence on the page that the shallow
  behavior is known to the authors. **One inference, clearly labeled as ours:**
  the page states that returned properties *replace* at the top level but never
  says whether *unreturned* top-level keys are preserved. The `beforeEach`
  session example returns `{ test: ... }` only, which is safe there solely
  because `beforeEach`'s context happens to contain only `test`; copying that
  shape into `afterEach` (whose context is `{ test, result }`) is undefined by
  the documentation. Practical rule for the guide: return the whole context
  object, the way the vendor's own examples do.

### Claim 4: The verdict is structurally protected from hooks — `success`, `score`, and `response.output` are explicitly **not** overridable from `afterEach`, leaving metadata and named scores as the entire writable surface
- **Evidence**: The `afterEach` property table enumerates three writable
  properties (`context.result.namedScores`, `context.result.metadata`,
  `context.result.response.metadata`) and then closes with the non-overridable
  sentence.
- **Confidence**: settled (documented product behavior; the deny-list is
  explicit, and it is the only such deny-list in the hook section)
- **Quote**: "Fields like `success`, `score`, and `response.output` are not overridable from `afterEach`."
- **Our assessment**: Buy it, and read it as a security property rather than a
  limitation — it is the eval-gate analogue of fail-closed grading. A hook that
  wants to rescue a failing row cannot do it through the verdict; it can only
  attach context (`metadata`) or custom metrics (`namedScores`, e.g.
  `num_turns` / `cost_usd`). So the *per-row verdict* cannot be gamed from
  operator code, which is a stronger guarantee than the corpus's other
  promptfoo gating findings — `PROMPTFOO_FAILED_TEST_EXIT_CODE` can make a
  failing eval exit `0`, and `PROMPTFOO_PASS_RATE_THRESHOLD` can fail an
  all-green-per-case suite (`docs-promptfoo-configuration-outputs.md` Claim 10),
  and `PROMPTFOO_CACHE_ENABLED` / cache TTL decide whether the run calls the
  model at all (`docs-promptfoo-configuration-caching.md` Claims 1 and 4). The
  correct synthesis is: *the row is hard, the gate around the row is soft, and
  a hook is not a way to move the row.* Two caveats to keep: "Fields **like**"
  is an illustrative list, not a closed one, so the protected set is
  documented as examples rather than exhaustively enumerated; and the
  non-overridability is stated only for `afterEach`, so what `beforeEach` may
  do to a verdict it has not seen yet, and whether `beforeAll` could set a
  suite-level default that effectively grants a pass, is not stated.

### Claim 5: Registration is name-sensitive, not just path-sensitive — the function name after the colon selects the calling convention, and a function whose name is *not* a hook name receives all four event types
- **Evidence**: The `extensions` `Config` row, the `important` admonition in
  "Implementing Hooks", the `note` admonition on calling conventions, and the
  "Example configuration" block.
- **Confidence**: settled (documented product behavior; the rule is stated
  once, in an admonition, and illustrated)
- **Quote**: "A custom function name receives all event types (`beforeAll`, `afterAll`, `beforeEach`, `afterEach`) with the legacy `(hookName, context)` calling convention. If the function name is exactly one of the hook names, promptfoo only runs it for that hook and calls it as `(context, { hookName })`."
- **Quote**: "When specifying an extension in the configuration, you must include the function name after the file path, separated by a colon (`:`). This tells promptfoo which function to call in the extension file."
- **Our assessment**: Buy it, with a sharp operational edge. The overload is
  invisible at the registration site: `file://ext.js:extensionHook` and
  `file://ext.js:afterEach` both parse, but the second binds the function to
  one hook and swaps the argument order — so renaming a working
  all-events dispatcher to `afterEach` (a natural refactor when you only ever
  cared about one stage) silently changes its signature, and the body reads
  `context.suite.description` where `context` is now a `TestCase`. That is an
  immediate, loud failure rather than a silent one, which is the good news;
  the bad news is the inverse — a hook written against the modern
  `(context, { hookName })` convention but registered under a non-hook name
  gets `hookName` bound to a context object and fails the same way. This is
  the same `file://` + `:functionName` selector convention that
  `docs-promptfoo-javascript-assertions.md` Claim 8 owns for assertion scripts;
  here it carries the additional name→dispatch binding, which that note does
  not document. Note also that the page supports `.py` as a first-class peer of
  `.js`, so the "write a hook" path is not gated on a Node toolchain.

### Claim 6: Session-id resolution is a documented two-step fallback with a fixed precedence — a provider-returned `response.sessionId` always wins over the test-config `vars.sessionId`, and for HTTP targets the id is manufactured by a `sessionParser` expression on the response
- **Evidence**: The "Test-Time Session Definition" subsection — two paragraphs,
  a provider-config example, the "made available in the `afterEach` hook
  context" pointer, the precedence **Note**, and the `sessionParser` example.
- **Confidence**: settled (documented product behavior; the precedence is
  stated as an explicit ordering)
- **Quote**: "Session ids returned by your provider in `response.sessionId` will be used as the session id for the test case. If the provider does not return a session id, the test variables (`vars.sessionId`) will be used as fallback."
- **Quote**: "The priority is: `response.sessionId` > `vars.sessionId`."
- **Quote**: "For HTTP providers, you extract session IDs from server responses using a `sessionParser` configuration. The session parser tells promptfoo how to extract the session ID from response headers or body, which then becomes `response.sessionId`."
- **Quote** (HTTP provider example): "sessionParser: 'data.headers[\"x-session-id\"]'"
- **Our assessment**: Buy it — and this is the claim with the sharpest
  cross-document failure mode, because it collides with the vendor's *own*
  recommended session pattern on the same page. The page tells you to create a
  server-side session in `beforeEach`, write its id into `vars.sessionId`, and
  read it back in `afterEach` for cleanup (`const id = context.test.vars.sessionId`).
  If the target under test *also* returns a session id — which for HTTP
  providers the page immediately shows you how to configure via
  `sessionParser` — then the effective session is the provider's, while
  `afterEach` still deletes `context.test.vars.sessionId`. Result: you clean up
  the pre-created session, track the provider's, and leak whichever one the
  target minted. Nothing warns; both sides of the page are individually
  correct. The guide should state the ordering as a rule for authors of
  stateful evals: pick **one** session owner per target — either
  `beforeEach`-created ids in `vars.sessionId` (and no `sessionParser`), or
  provider-returned ids (and no pre-created session) — because the page's
  precedence makes the second silently outrank the first while leaving the
  first's cleanup path intact. Also worth stating for Ch02/Ch06: the id that
  hooks read is not the id the provider necessarily used, so
  `context.result.metadata.sessionId` is the only trustworthy correlator for
  trace-to-session joins.

### Claim 7: Iterative red-team strategies expose a **different** session field — `context.result.metadata.sessionIds`, an array of per-iteration ids that silently drops iterations without a session id, so array position is not iteration identity
- **Evidence**: The "For iterative red team strategies" paragraph, its
  "Example usage for iterative providers" code block, and the closing **Note**.
- **Confidence**: settled (documented product behavior; the filtering rule is
  called out in its own note)
- **Quote**: "For iterative red team strategies (e.g., jailbreak, tree search), the `sessionIds` array is made available in the `afterEach` hook context at: `context.result.metadata.sessionIds`"
- **Quote**: "Note: The `sessionIds` array only contains defined session IDs - any iterations without a session ID are filtered out."
- **Our assessment**: Buy it, and flag the correlation hazard the page's own
  example walks into. The page's example logs
  `` `  Iteration ${index + 1}: session ${id}` `` — i.e. it presents the array
  index as the iteration number — while the note says undefined-id iterations
  are *filtered out* of the array. The two are only consistent when every
  iteration has a session id. When any iteration does not (exactly the case a
  red-team run is most likely to hit, since a crashed or non-conversational
  iteration may produce none), the printed "Iteration *k*" labels are off —
  session from attempt 3 is logged as "Iteration 2" — so the attack path you
  reconstruct from hook logs can silently misattribute which attempt produced
  the bypass. For Ch06 this is a concrete rule: treat `sessionIds` as an
  unordered *set* of ids to join on, never as an index into the iteration
  sequence, and prefer whatever per-iteration metadata the strategy itself
  writes over array position. The two-field split (`sessionId` for regular
  providers, `sessionIds` for iterative ones) also means a hook that reads only
  the singular field goes empty on every jailbreak/tree-search run with no
  error — the same silent-divergence class as Claim 3.

### Claim 8: `filterSampleSeed` is promptfoo's documented reproducibility knob for sampled suites — without it `filterSample` draws a *different* subset on every run, so two CI runs of the same commit grade different test populations
- **Evidence**: The `filterSample` and `filterSampleSeed` rows of the
  `CommandLineOptions` "Filtering" group, and the worked `commandLineOptions`
  example on the same page.
- **Confidence**: settled (documented product behavior; both rows are
  explicit, and the example supplies a concrete seed)
- **Quote**: "Numeric seed used to make `filterSample` select the same test cases on repeated runs"
- **Quote** (worked `promptfooconfig.yaml` on this page, the two adjacent lines as written):
  "filterSample: 50 # Random sample of 50 tests" and
  "filterSampleSeed: 42 # Repeat the same random sample"
- **Our assessment**: Buy it, and note that it is the *only* determinism knob
  in the filtering group — `filterSample` is the sole random-sampling control
  and it is the one control that changes the population rather than the
  execution. This is a CI-gate correctness issue, not a performance one: a
  commit can be red on run 1 (a sampled case that was not selected on run 2),
  or green on run 1 and red on run 2, with an identical config, an identical
  commit, and a byte-identical reason string that names a different test case.
  That makes "flaky gate" indistinguishable from "gate with unstable
  membership" — precisely the class of ambiguity the guide's "a green eval is
  not evidence" theme is about. It also completes a determinism picture the
  corpus only has one corner of: `docs-promptfoo-configuration-rate-limits.md`
  Claim 9 documents the *execution*-side determinism recipe
  (`maxConcurrency: 1` + `delay: 1000`), and this row is the *membership*-side
  one. Both are needed for a repeatable gate, and neither substitutes for
  `--no-cache` (`docs-promptfoo-configuration-caching.md` Claim 8).

### Claim 9: `suggestionsCount` (default `1`, max `50`) turns on prompt-set mutation — `generateSuggestions` appends generated variants to the prompt list, and the `GradingResult` suggestions interface on the same page names `replace-prompt` as a suggestion action, so the harness can propose edits to the very prompts it is grading
- **Evidence**: The `generateSuggestions` and `suggestionsCount` rows of the
  `CommandLineOptions` "Prompt Modifications" group, plus the
  `ResultSuggestion` interface in the `GradingResult` section of the same page.
- **Confidence**: settled (documented product behavior; default and cap are
  stated numerically)
- **Quote**: "Generate new prompts and append them to the prompt list"
- **Quote**: "Number of prompt variations to generate when `generateSuggestions` is enabled (default `1`, max `50`). May also be set under `evaluateOptions`; the CLI flag `--suggest-prompts <n>` is equivalent."
- **Quote**: "interface ResultSuggestion { type: string; action: 'replace-prompt' | 'pre-filter' | 'post-filter' | 'note'; value: string;}"
- **Our assessment**: Buy it as a field default plus one structural point, and
  be explicit that this claim is thin — a single-row default, flagged by triage
  as include-only-if-thin. The default of `1` is low-risk; the cap of `50` is
  not, because the effect is on the *denominator*: `generateSuggestions`
  appends to `prompts`, so one flag can add up to 50 variants to the prompt set
  a CI run grades, changing per-prompt metrics and every `PROMPTFOO_PASS_RATE_THRESHOLD`
  denominator
  (`docs-promptfoo-configuration-outputs.md` Claim 10) without a single line of
  the prompt config changing. The structural point is that the page's own
  `ResultSuggestion` vocabulary includes `replace-prompt`, `pre-filter`, and
  `post-filter` — i.e. the suggestion channel is defined to propose edits to
  prompts and to insert filters around them, which is the eval harness
  operating on its own subject under test. We are **not** claiming a documented
  auto-apply loop: the page never states that suggestions are applied
  automatically, and it is not stated anywhere in the corpus that they are.
  Recorded as a surface to be aware of, not a mechanism.

## Concrete Artifacts

### Available Hooks table (verbatim from "Extension Hooks" > "Available Hooks")

| Name        | Description                             | Context                                                                                                                 |
| ----------- | --------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `beforeAll` | Runs before the entire test suite begins | `{ suite: TestSuite }`                                                                                                   |
| `afterAll`  | Runs after the entire test suite has finished | `{ results: EvaluateResult[], prompts: CompletedPrompt[], suite: TestSuite, evalId: string, config: Partial<UnifiedConfig> }` |
| `beforeEach` | Runs before each individual test        | `{ test: TestCase }`                                                                                                     |
| `afterEach` | Runs after each individual test         | `{ test: TestCase, result: EvaluateResult }`                                                                            |

*(Attribution: promptfoo docs "Configuration > Reference" > "Extension Hooks" > "Available Hooks".)*

**The persistence rule and the shallow-merge rule, verbatim and adjacent**
(same page, end of "Implementing Hooks"):

> The `beforeAll`, `beforeEach`, and `afterEach` hooks may mutate specific
> properties of their respective `context` arguments in order to modify
> evaluation state. To persist these changes, the hook must return the modified
> context.
>
> All merges are shallow: returned properties replace existing values at the
> top level. Nested objects (e.g., `metadata: { nested: { a: 1 } }`) are
> replaced entirely, not deep-merged.

**The `afterEach` writable surface** (verbatim from the `afterEach` property
table, followed by the sentence that closes the section):

| Property                         | Type                     | Description                                            |
| -------------------------------- | ------------------------ | ------------------------------------------------------ |
| `context.result.namedScores`      | `Record<string, number>` | Custom numeric metrics (e.g., `num_turns`, `cost_usd`). |
| `context.result.metadata`         | `Record<string, any>`    | Structured data (e.g., tool call details, URLs).       |
| `context.result.response.metadata` | `Record<string, any>`   | Response-level metadata (e.g., session viewer URLs).   |

> Fields like `success`, `score`, and `response.output` are **not** overridable
> from `afterEach`.

**The vendor's own `beforeEach` session example** (JavaScript, from "Pre-Test
Session Definition") — note the spread-then-override shape, which is the only
demonstration on the page of writing the shallow merge correctly, and the
`afterEach` branch that cleans up by reading the id back out of `vars`:

```javascript
export async function extensionHook(hookName, context) {
  if (hookName === 'beforeEach') {
    const res = await fetch('http://localhost:8080/session');
    const sessionId = await res.text();
    return { test: { ...context.test, vars: { ...context.test.vars, sessionId } } }; // Scope the session id to the current test case
  }
  if (hookName === 'afterEach') {
    const id = context.test.vars.sessionId; // Read the session id from the test case scope
    await fetch(`http://localhost:8080/session/${id}`, { method: 'DELETE' });
  }
}
```

**HTTP `sessionParser` — the config that manufactures `response.sessionId`**
(same page, "Test-Time Session Definition"):

```yaml
providers:
  - id: http
    config:
      url: 'https://example.com/api'
      # Session parser extracts ID from response → becomes response.sessionId
      sessionParser: 'data.headers["x-session-id"]'
      headers:
        # Use the extracted session ID in subsequent requests
        'x-session-id': '{{sessionId}}'
```

**The iterative-strategy example, including the index-as-iteration-label pattern
discussed in Claim 7** (same page, "Example usage for iterative providers"):

```javascript
async function extensionHook(hookName, context) {
  if (hookName === 'afterEach') {
    // For regular providers - single session ID
    const sessionId = context.result.metadata.sessionId;
    // For iterative providers (jailbreak, tree search) - array of session IDs
    const sessionIds = context.result.metadata.sessionIds;
    if (sessionIds && Array.isArray(sessionIds)) {
      console.log(`Jailbreak completed with ${sessionIds.length} iterations`);
      sessionIds.forEach((id, index) => {
        console.log(`  Iteration ${index + 1}: session ${id}`);
      });
      // You can use these sessionIds for detailed tracking of the attack path
    }
  }
}
```

**Registration and calling convention** (same page, "Example configuration" and
the `important` / `note` admonitions):

```yaml
extensions:
  - file://path/to/your/extension.js:extensionHook
  - file://path/to/your/extension.py:extension_hook
```

> A custom function name receives all event types (`beforeAll`, `afterAll`,
> `beforeEach`, `afterEach`) with the legacy `(hookName, context)` calling
> convention. If the function name is exactly one of the hook names, promptfoo
> only runs it for that hook and calls it as `(context, { hookName })`.

**Sampling reproducibility, from the page's worked `promptfooconfig.yaml`
`commandLineOptions` example:**

```yaml
  filterSample: 50 # Random sample of 50 tests
  filterSampleSeed: 42 # Repeat the same random sample
```

**Prompt-set mutation rows** (verbatim from `CommandLineOptions` > "Prompt
Modifications"):

| Property             | Type      | Description                                                                                                                                                    |
| -------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `generateSuggestions` | `boolean` | Generate new prompts and append them to the prompt list                                                                                                          |
| `suggestionsCount`    | `integer` | Number of prompt variations to generate when `generateSuggestions` is enabled (default `1`, max `50`). May also be set under `evaluateOptions`; the CLI flag `--suggest-prompts <n>` is equivalent. |

*(Attribution: promptfoo docs "Configuration > Reference" > "CommandLineOptions" > "Prompt Modifications".)*

## Cross-References

All citations below were verified by re-reading the cited note and locating the
numbered claim (MINER.md §4b). Claim numbers are document-order counts.

- **Extends**:
  - `docs-promptfoo-javascript-assertions.md` **Claim 8** owns the
    `file://path/script.js` + optional `:functionName` selector convention for
    *assertion* scripts. This note extends it to extension files and adds the
    part that note does not document: the function **name** selects the calling
    convention (all-events legacy `(hookName, context)` vs single-hook
    `(context, { hookName })`) — our Claim 5. Same `file://:fn` machinery,
    different dispatch semantics.
  - `docs-promptfoo-configuration-guide.md` **Claim 2** owns the corpus's prior
    instance of the "replacement, not composition" class (a per-case
    `options.transform` **overrides** the `defaultTest` one). Our Claim 3 is
    the same class at a different layer — a hook's returned context replaces
    nested objects rather than deep-merging — and is the more dangerous
    instance because it sits on the `metadata` path that reporting hooks use.
  - `docs-promptfoo-configuration-rate-limits.md` **Claim 9** owns the
    *execution-side* determinism recipe (`maxConcurrency: 1` + `delay: 1000`).
    Our Claim 8 is the *membership-side* knob (`filterSampleSeed`) and neither
    substitutes for the other.
- **Corroborates**:
  - `docs-promptfoo-llm-rubric.md` **Claim 8** is the only pre-existing corpus
    mention of `afterEach`, and it uses the hook as a *metadata consumer*
    ("which makes per-assertion fields such as upload IDs or trace IDs
    available in hooks like afterEach"). Our Claim 4 names the actual surface
    that makes this work — `context.result.metadata` /
    `context.result.response.metadata` / `context.result.namedScores` are
    writable from `afterEach` — and adds the constraint that note does not
    mention: the verdict fields in the same object are not writable. This note
    supplies the mechanism behind that note's aside; no conflict.
  - `docs-promptfoo-configuration-caching.md` **Claims 1 and 4** corroborate the
    broader framing in our Guide Impact that a promptfoo gate's greenness is a
    function of ambient settings: caching is on by default with a 14-day TTL, so
    even with `filterSampleSeed` pinned (Claim 8) a run may replay cached
    responses rather than calling the model.
- **Contradicts**: none. No claim in this note opposes an existing note, and
  the source does not disagree with itself. Two candidates were checked and
  rejected as contradictions: (a) `docs-promptfoo-chat-threads.md` **Claim 1**
  states that `_conversation` forces single-threaded execution with "no config
  knob to restore it", while this page's `options.runSerially` row reads "If
  true, run this test case without concurrency regardless of global settings" —
  these are not in conflict, since `runSerially` is an opt-*in* to
  serialization, not a way to undo implicit serialization; (b) this page's
  `Guardrails` paragraph (`flaggedInput: true` or `flaggedOutput: true` without
  `flagged: true` is "diagnostic only and does not fail the assertion"; missing
  signal "does not prove that a guardrail ran") is fully owned by
  `docs-promptfoo-guardrails-assertions.md` **Claims 2, 3, and 8** and is
  deliberately not re-extracted here — same content, not a conflict.
- **Novel** (zero prior corpus coverage, verified by grep over all 224 notes):
  the entire extension-hook lifecycle (`extensions` field, the four hooks and
  their disjoint context shapes, the mutate-and-return persistence rule, the
  shallow-merge contract, the non-overridable verdict fields, and the
  name-dependent calling convention); session-id management in hooks at all
  (`response.sessionId` > `vars.sessionId`, `sessionParser`,
  `context.result.metadata.sessionId`, and the iterative
  `context.result.metadata.sessionIds` array with its undefined-id filtering);
  `filterSampleSeed`; and `suggestionsCount` / `generateSuggestions`. No
  promptfoo note in the corpus contains the strings `retryErrors`,
  `filterSampleSeed`, `suggestionsCount`, `runSerially`, `sessionId`, or
  "Extension Hooks" before this note.
- **Candidate dismissals** (from `miner-related-notes.md`, all read and checked
  against this note's claims): `docs-promptfoo-pi-scorer.md` (external
  model-graded `pi` scorer — unrelated to the eval lifecycle), `docs-langfuse-mcp-server.md`
  (docs-over-MCP transport), `docs-google-sre-team-lifecycles.md` (org/role
  design), `blog-promptfoo-owasp-red-teaming.md` (red-team process guidance;
  thematically adjacent to Claim 7's iterative strategies but shares no claim),
  `docs-litellm-batches-api.md` (gateway rate limiting),
  `blog-pagerduty-sre-agent-triage.md` (LLM-judge alerting — adjacent to Ch05's
  gate theme but shares no claim with this page),
  `docs-promptfoo-classifier-grading.md` (HuggingFace classifier grading),
  `docs-google-sre-eliminating-toil.md` (toil taxonomy; hooks are conceptually
  an automation of setup/teardown, but no shared claim). Two candidates *are*
  cited above: `docs-promptfoo-javascript-assertions.md` and
  `docs-promptfoo-llm-rubric.md`.

## Guide Impact

- **Ch05 (LLM Ops Reliability)**: add the hook lifecycle as a bounded
  extension surface in the eval-configuration material, with three specific
  statements. (a) A hook's verdict is hard but the gate around it is soft:
  `success`, `score`, and `response.output` are not overridable from
  `afterEach` (Claim 4), while `PROMPTFOO_FAILED_TEST_EXIT_CODE` /
  `PROMPTFOO_PASS_RATE_THRESHOLD` (per `docs-promptfoo-configuration-outputs.md`
  Claim 10) and `PROMPTFOO_CACHE_ENABLED` (per
  `docs-promptfoo-configuration-caching.md` Claims 1/4) still decide whether the
  suite goes green. (b) Two silent config-shaped greenness bugs to add to the
  chapter's "a green eval is not evidence" list: `filterSample` without
  `filterSampleSeed` makes each CI run grade a different test population
  (Claim 8), and `generateSuggestions` appends up to `50` new prompts to the
  graded set, changing the pass-rate denominator without any change to the
  prompt config (Claim 9). (c) Determinism requires *both* the execution-side
  recipe (`maxConcurrency: 1` + `delay`, per
  `docs-promptfoo-configuration-rate-limits.md` Claim 9) and the membership-side
  `filterSampleSeed`, plus `--no-cache` — no single knob suffices.
- **Ch05 / Ch02 (Observability)**: the hook contract is the documented seam for
  joining eval rows to external state. `afterEach` can attach
  `context.result.metadata` and custom `namedScores` (e.g. `num_turns`,
  `cost_usd`) but not rewrite the row, which makes it the fail-closed place to
  stamp correlation IDs (Claims 1, 4). The chapter's trace-correlation advice
  should use `context.result.metadata.sessionId` as the trustworthy
  eval-row-to-conversation key and treat it as distinct from
  `context.test.vars.sessionId` (Claim 6).
- **Ch06 (Security and Trust)**: for red-team (jailbreak, tree-search) suites,
  `afterEach` sees `context.result.metadata.sessionIds`, not `sessionId`
  (Claim 7), and the array drops iterations without an id — so attack-path
  reconstruction must join on the id set and must not read array position as
  iteration number. Also state the session-ownership rule from Claim 6:
  `response.sessionId` outranks `vars.sessionId`, so a target that returns its
  own session id silently defeats the `beforeEach`-created-session cleanup the
  same page recommends, leaking a server-side session while the eval tracks a
  different one.
- **New content worth adding (no chapter owns it today)**: the "documented
  divergence between config appearance and behavior" class deserves one named
  subsection with all corpus instances collected — the shallow-merge contract
  (Claim 3), the transform override (per
  `docs-promptfoo-configuration-guide.md` Claim 2), the guardrail fail-open
  default (per `docs-promptfoo-guardrails-assertions.md` Claim 3), and the
  transform/audio degradation trap (per `docs-promptfoo-llm-rubric.md` Claim 3).
  The common shape: a field reads as "compose/extend" and behaves as
  "replace/ignore", with no error. Recommend the guide name this class
  explicitly and give readers a checklist of "looks additive, is not"
  fields.
- **Do not add**: the page's schema tables, the `evaluateOptions` /
  `CommandLineOptions` inventory beyond the two defaults cited, and the
  TypeScript interface dumps. `retryErrors`, `filterErrorsOnly` /
  `filterFailing` / `filterFailingOnly`, `timeoutMs` / `maxEvalTimeMs`,
  `maxConcurrency` / `delay`, `basePath`, `env` / `envPath`, `cache`, and
  `storeOutputAs` are already owned by the sibling notes cited above and must
  not be synthesized a second time.

## Extraction Notes

- **Scope discipline**: the Prospector triaged this issue three times (three
  triage comments, all pointing at the same residual). All three named the
  Extension Hooks lifecycle as the one item of real weight and the
  session-id precedence as novel; one added the redteam `suggestionsCount`
  field. This note covers exactly that residual (Claims 1–7, 9) plus one
  item beyond the triage list: `filterSampleSeed` (Claim 8). That addition was
  made deliberately and is disclosed here — it is a `commandLineOptions` row,
  and the third triage comment advised treating the property tables as schema
  listings "with no defaults, semantics, or failure modes beyond the fields
  named here". `filterSampleSeed` *has* a default-free but
  semantics-bearing row ("select the same test cases on repeated runs") and a
  worked example with a concrete seed, and it feeds the guide's central
  greenness theme, so it is included rather than omitted. Every other schema
  row was skipped.
- **Explicitly NOT re-extracted** (owned elsewhere; verified against the cited
  notes before skipping): the transformation pipeline and its three-stage
  ordering (Claim 1 of `docs-promptfoo-configuration-guide.md` #1513, whose
  Extraction Notes already record this page as a cited linked reference);
  `evaluateOptions.timeoutMs` / `maxEvalTimeMs` and
  `filterErrorsOnly` / `filterFailing` / `filterFailingOnly` (Claim 9 of
  `docs-promptfoo-configuration-outputs.md` #1528, which also owns the
  error-vs-failure split and the `promptfoo retry` subcommand — note the
  `retryErrors` row on this page ("Retry all ERROR results from the latest
  eval") is that note's territory and was **not** re-claimed here);
  `maxConcurrency` / `delay` / retry-backoff env vars
  (`docs-promptfoo-configuration-rate-limits.md`); `basePath` path resolution
  (`docs-promptfoo-modular-configs.md` #1527); the `flagged` /
  `flaggedInput` / `flaggedOutput` fail-open semantics
  (`docs-promptfoo-guardrails-assertions.md` #1303, Claims 2/3/8);
  `storeOutputAs` (`docs-promptfoo-chat-threads.md` #1276, Claim 4); the
  `cache` default and replay semantics (`docs-promptfoo-configuration-caching.md`
  #1275); `disableDefaultAsserts` / `disableVarExpansion` / `config.env`
  (Claims 6, 12, 7 of `docs-promptfoo-configuration-guide.md`).
- **Reading depth**: the page was read in full (rendered markdown) and every
  quoted passage was then re-verified character-for-character against the raw
  HTML of the same URL, because the markdown render strips `**` emphasis
  markers and normalizes some dashes — quotes here reproduce the raw page text
  without emphasis markup, matching the convention in
  `docs-promptfoo-configuration-guide.md`. No sub-pages were followed: the
  extension-hooks section is self-contained on this page. Its one external
  pointer (`/docs/providers/http/#session-management`, for the full
  `sessionParser` surface) was left unmined and is a genuine gap — no note in
  the corpus covers the HTTP provider's session management, which is where the
  provider-side id in Claim 6 actually comes from.
- **What the source does not say** (flagged rather than inferred): whether a
  throwing hook fails, errors, or is swallowed (Claim 2a); whether top-level
  context keys the hook does *not* return are preserved or dropped (Claim 3,
  labeled as our inference); whether the non-overridable field list is closed
  (the page says "Fields like", i.e. illustrative); what `beforeAll` may do to
  verdicts it has not yet seen (Claim 4); and whether `ResultSuggestion`
  entries are ever applied automatically (Claim 9 — no such statement on this
  page or anywhere in the corpus).
- **Contradiction check performed**: §4a reviewed against all open
  `contradiction`-labeled issues and `CONTRADICTIONS.md` before writing. No
  qualifying contradiction found (see Cross-References → Contradicts), so no
  contradiction issue was filed. Two near-misses were examined and rejected
  under §4a's "when NOT to file" rule as conditioning variables, not
  disagreements.
- **Novelty check**: `grep` across all 224 files in `source-notes/` for
  `retryErrors`, `filterSampleSeed`, `suggestionsCount`, `runSerially`,
  `sessionId`, `Extension Hooks`, and `shallow` confirms this surface was
  genuinely unmined. The only pre-existing `afterEach` hit is
  `docs-promptfoo-llm-rubric.md` Claim 8 (a consumer, not the lifecycle), and
  the only `sessionId` hits are in unrelated LiteLLM/Langfuse notes.
- **Confidence**: `settled` for the hook contract, session precedence, and
  field defaults — all are explicit first-party statements about the tool's own
  behavior, each independently checkable against an installed CLI. Downgraded
  from a blanket `settled` only in the sense that individual *consequences*
  flagged in Our assessment (hook-error behavior, partial-context merge, array
  index ≠ iteration) are inferences from these statements rather than
  documented claims, and are labeled as such.