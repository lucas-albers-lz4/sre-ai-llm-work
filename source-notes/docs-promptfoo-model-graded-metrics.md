---
source_url: https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/
source_type: docs
title: "Promptfoo Configuration: Model-Graded Metrics"
author: "Promptfoo (vendor documentation)"
date_published: 2026-09-14
date_extracted: 2026-09-14
last_checked: 2026-09-14
status: current
confidence_overall: emerging
issue: "#1305"
---

# Promptfoo Configuration: Model-Graded Metrics

> The vendor reference for every assertion type that puts an LLM judge (or an
> agentic/web-search grader) inside the eval gate — and the page that answers
> the hub note's (#1287) open question of what is actually pinned behind a
> model-graded assert: nothing, by default. The judge model is selected from
> ambient environment credentials, an assertion-level shorthand provider
> silently disables the global provider object's `config`, reasoning can leak
> into graded `content` (with `showThinking: false` and a vLLM-specific
> unfinished-`thinking`-block caveat), `trajectory:goal-success` fails closed
> under `not-` inversion but that fail-closed property is documented only for
> the inverted form, and a rubric-less `llm-rubric` passes on the judge's
> `pass` field alone (defaulting to `true`) — score 0 passes without a
> threshold.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Model-graded
  metrics" assert-type reference page under `/docs/configuration/expected-outputs/`)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner). First-party documentation of the
  tool's own judge-grader behavior — authoritative for *what promptfoo does*
  with a given model-graded config (the default judge selection, the override
  precedence, the `showThinking` handling, the pass/score semantics), but
  vendor-positioned: the page carries no measured gate-failure-rate, judge
  agreement, cost, or calibration figures, and there is no independent
  practitioner validation. Everything below is checkable against an installed
  CLI. Whether a judge gate is *trustworthy in practice* is asserted by the
  vendor only (e.g., the fail-closed inversion is a design statement, not a
  measured property).
- **Scope**: The "Model-graded metrics" hub page under "Assertions & metrics"
  — the last sibling of the `expected-outputs` sub-page family whose other two
  members (#1287 hub scoring/aggregation, #1288 classifier, #1289 deterministic)
  are already mined. Covers the output/context/conversational/trajectory
  model-graded type catalogue, `trajectory:goal-success` (the first
  trajectory-based model-graded assert), the LLM-grader override mechanism
  (`--grader` CLI / `test.options.provider` / `assertion.provider` and the
  shorthand-provider `config`-inheritance trap), OpenAI-compatible thinking
  judges (`showThinking: false`, vLLM caveat), `rubricPrompt` overrides
  (multilingual, image-based, `select-best`), context-based RAG assertions and
  `contextTransform`, comparison types (`select-best`, `max-score`), and the
  pass-vs-score semantics. Two linked sub-pages the triage flagged as novel
  capability surfaces (`agent-rubric`, `search-rubric`) were followed for their
  config semantics; the remaining per-type sub-pages (g-eval, pi, llm-rubric,
  model-graded-closedqa, factuality, answer-relevance, conversation-relevance,
  context-*, max-score, select-best) were not followed — they are per-type
  reference pages and consistent with the sibling extraction convention.
- **Last updated**: Sep 14, 2026 by renovate[bot]; the page is undated but the
  documented examples describe the current `gpt-5` era.

## Extracted Claims

### Claim 1: By default, the judge behind every model-graded assertion is unpinned — promptfoo's built-in grading provider picks its model from whichever credentials happen to be present in the environment, so the judge can change when the environment changes without any config edit
- **Evidence**: The "Overriding the LLM grader" section's opening paragraph,
  which names OpenAI, Anthropic, Gemini, Mistral, Azure OpenAI, and Codex login
  credentials as alternative ambient defaults.
- **Confidence**: settled (documented product behavior)
- **Quote**: "By default, model-graded asserts use promptfoo's built-in grading provider. Promptfoo chooses that provider from the credentials available in the environment; for example, OpenAI, Anthropic, Gemini, Mistral, Azure OpenAI, and Codex login credentials can each activate a different default."
- **Our assessment**: This is the headline finding the sibling notes left open.
  #1287's hub note ended on "the residual unpinned inputs are the judge models
  behind model-graded assertions" — this page answers that thread with the
  mechanism: the judge is ambient, not pinned. For an eval gate this is a
  reproducibility hazard of the worst kind: an unset `OPENAI_API_KEY` (or a new
  `ANTHROPIC_API_KEY` added to a runner) silently swaps the grader mid-life of a
  config that is otherwise untouched. The Clrepermancy is asymmetric too — a CI
  gate that pins the *target* model but not the *judge* is half-pinned, and the
  judge is the half that decides the verdict. Any Ch05 gate-review rule that
  requires pinning must explicitly cover grader selection.

### Claim 2: Grader overrides resolve by precedence `--grader` CLI → `test.options`/`defaultTest.options.provider` → `assertion.provider` — and an assertion-level *shorthand* provider quietly blocks inheritance of the global provider object's `config` (`apiBaseUrl`, `apiKey`, `temperature`, `showThinking`)
- **Evidence**: The three numbered override forms in the "Overriding the LLM
  grader" section plus the explicit warning paragraph about shorthand
  providers at assertion level.
- **Confidence**: settled (documented product behavior, with the vendor's own warning)
- **Quote**: "If you configure a full provider object globally, do not also add a shorthand `provider: openai:chat:...` to the assertion. Assertion-level providers take precedence, so the global provider object's `config` values such as `apiBaseUrl`, `apiKey`, `temperature`, or `showThinking` will not be inherited. Either remove the assertion-level provider or repeat the full provider object there."
- **Our assessment**: The concrete "silent misroute" trap the triage highlighted.
  The failure is invisible in the report: the judge still runs, it just grades
  from the wrong endpoint/credentials (e.g., a self-hosted judge with
  `showThinking: false` globally, then one assertion adds
  `provider: openai:chat:...` and silently loses the `showThinking`/`apiBaseUrl`
  config while the run stays green). This is exactly the config-level mechanism
  behind the guide's judge-trust rules: the override precedence must be
  reviewed as a whole (grep every level), because the effective grader is the
  most-specific level, not the most-recently-authored one.

### Claim 3: `trajectory:goal-success` is the trajectory-based model-graded assert — it requires trace data, summarizes the traced run and its final output, and asks a grading model whether the specified goal was achieved, with `threshold`/`provider`/`rubricPrompt` supported like other model-graded assertions
- **Evidence**: The "trajectory:goal-success" section's definition, the
  `tests`/`assert` config with `value: 'Determine the shipping status...'`, the
  threshold/provider variant (`openai:gpt-5.6`), and the cross-reference to the
  deterministic trajectory checks.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Use `trajectory:goal-success` when you care about whether an agent actually completed a task, not just whether it used a specific tool or produced a plausible final sentence." and "This assertion requires trace data. Promptfoo summarizes the traced trajectory, includes the final output, and asks a grading model whether the run achieved the goal you specify."
- **Our assessment**: The eval side of agent-goal verification (Ch03), and the
  series' first *model-judged* trajectory assert (the hub note #1287 Claim 11
  already catalogs it with the judge-variance caveat). Two operational
  couplings: it consumes the OTel-shaped trace (per the honeycomb note's span
  schema contract, #2 Claims 2/12), so the gate inherits the tracing pipeline's
  health — the deterministic sibling #1289 Claim 12 documents that missing trace
  data makes the built-in trace family *throw*; and its verdict depends on an
  unpinned judge (Claim 1) unless `provider:` is set. The page's pairing
  guidance — run it beside `trajectory:tool-used` / `:tool-args-match` /
  `:tool-sequence` when the exact path matters — is the right "goal AND path"
  formulation for a release gate.

### Claim 4: `not-` inversion of `trajectory:goal-success` is fail-closed — inversion only flips real grader verdicts, so a judge transport/parse failure still reports as a failure instead of silently passing the "did not achieve forbidden goal" check; but this fail-closed property is documented only for the inverted form, not as a general property of all model-graded assertions
- **Evidence**: The "Prepend `not-`..." paragraph directly under the
  `trajectory:goal-success` example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Inversion only flips real grader verdicts — judge transport or parse failures still report as failures so a broken judge cannot silently turn into a passing \"did not achieve forbidden goal\" result."
- **Our assessment**: This is the highest-value mechanism on the page and it
  directly resolves the triage's key question: the fail-closed behavior is
  stated for the *negative* (forbidden-goal) path only. The asymmetry is the
  finding — a positive `trajectory:goal-success` gate documents no equivalent
  statement here, so a team cannot read "broken judges fail closed" off this
  page as a general law; it is pinned to the inverted form. For the guide's
  "judge trust" rules this is the right nuance: the negative gate cannot be
  waved through by a broken judge (deliberate design), but the guide should not
  generalize beyond what the vendor states. Note also the deliberate wording:
  *transport* and *parse* failures fail closed — this is the counterweight to
  the hub note's `threshold: 0` / `weight: 0` silent-green footguns (#1287
  Claims 3/4), which are config-level, not judge-level, and are not addressed
  by this page.

### Claim 5: Self-hosted OpenAI-compatible judges (vLLM, LocalAI, llamafile) need `showThinking: false` so promptfoo grades only the final `content`, and the misparse risk is not `llm-rubric`-specific — JSON-first metrics, `answer-relevance`, RAG metrics, and `select-best` can all read scratchpad/thinking text as if it were the verdict
- **Evidence**: The "OpenAI-compatible thinking judges" section and its
  cross-type warning paragraph, plus the vLLM-specific caveat.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Self-hosted OpenAI-compatible judges such as vLLM, LocalAI, and llamafile can return reasoning in a separate field while putting the final answer in `content`. Set `showThinking: false` on the judge provider so promptfoo uses only the final `content` for grading:" and "This is not specific to `llm-rubric`. JSON-first metrics can parse scratchpad JSON, `answer-relevance` can embed questions with `Thinking:` prepended, RAG metrics can score scratchpad sentences or attribution markers, and `select-best` can read a scratchpad number as the winning index."
- **Our assessment**: A silent judge-misparse failure mode with an ops
  consequence: the graded string is not the judge's verdict but its
  scratchpad, and because the eval still completes with a verdict, the run
  reports *wrong* rather than *error*. For a gate built on a self-hosted judge,
  `showThinking: false` is not optional polish — it is the difference between
  grading the answer and grading the reasoning. The page scoping it across the
  whole model-graded family (not just `llm-rubric`) matters: teams that only
  set it for their rubric asserts still expose their RAG/select-best asserts to
  scratchpad parsing.

### Claim 6: The vLLM caveat — `showThinking: false` only strips reasoning *after* vLLM parses it into a separate field, so too-small `max_tokens`/context can leave an unfinished ` thinking` block inside `content` that then parses as a verdict
- **Evidence**: The vLLM-specific paragraph and the pointer to the vLLM judge
  guide.
- **Confidence**: settled (documented product behavior)
- **Quote**: "For vLLM specifically, `showThinking: false` only removes reasoning after vLLM has parsed it into a separate field such as `reasoning_content`. If `max_tokens` or the server context window is too small, vLLM may return an unfinished ` thinking` block in `content`; increase the budget or disable thinking for judge requests."
- **Our assessment**: A truncated-judge response that still parses as a verdict
  is the exact failure the guide's "can your gate tell wrong from a model break?"
  checklist should cover. The remediation is operational (budget/sizing or
  disabling thinking at request time), not a config flip — so self-hosted judge
  capacity (context window, `max_tokens`) becomes part of the gate's
  correctness surface, not just its throughput surface. This is the mechanism
  behind "silent misgrade," distinct from Claim 5's cross-type scratchpad
  parsing: here the *content itself* is contaminated.

### Claim 7: The built-in OpenAI grader already runs at `temperature=0`, and GPT-5-series reasoning models ignore `temperature` entirely — so the usual "pin temperature=0 for determinism" reflex does not apply to the OpenAI judge path
- **Evidence**: The note block in the grader-override section.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The built-in OpenAI grader already uses `temperature=0` by default, so you only need to set it when overriding the grader with a custom `provider` block that would otherwise inherit a non-zero default. GPT-5 series reasoning models ignore `temperature` entirely." and "The built-in OpenAI grader may spend hidden reasoning tokens internally, but promptfoo receives the final grader output without private reasoning text prepended to the output string."
- **Our assessment**: Two pinning myths corrected at once. First, `temperature=0`
  is already the built-in default, so setting it is only necessary on custom
  `provider` blocks. Second, on reasoning models the knob does nothing at all —
  determinism-obsessed teams that "pin temperature" for their GPT-5 judge are
  pinning nothing. The hidden-reasoning-tokens note is why the built-in OpenAI
  grader does *not* need `showThinking: false` (unlike self-hosted judges,
  Claim 5): private reasoning is consumed upstream and not prepended to the
  string promptfoo sees. Worth stating as the "judge determinism knobs" summary
  in Ch05 next to the judge-pinning rules from #261.

### Claim 8: A custom `rubricPrompt` under `defaultTest.options` is the documented route for multilingual grading, but it can only be swapped uniformly for `llm-rubric`, `g-eval`, and `model-graded-closedqa` — `factuality` and `context-recall` require assertion-specific prompts and specific output formats
- **Evidence**: The "Non-English Evaluation" section: the German `rubricPrompt`
  example (`defaultTest.options.rubricPrompt` with `{{ output }}` / `{{ rubric }}`
  and a JSON output instruction), the German reasoning output example, and the
  constraint note.
- **Confidence**: settled (documented product behavior)
- **Quote**: "This approach works with `llm-rubric`, `g-eval`, and `model-graded-closedqa`. Other assertions like `factuality` and `context-recall` require specific output formats and need assertion-specific prompts."
- **Our assessment**: The override reach is assertion-family-specific, which is
  the actionable constraint for a polyglot gate: teams can re-skin the prompt
  for the rubric/closedqa family but cannot uniformly replace the judge prompt
  across the model-graded tier. The mechanism also demonstrates the
  `{{ output }}` / `{{ rubric }}` template variables that custom rubrics bind to
  (see Concrete Artifacts), and the ISO-grade claim that the same `rubricPrompt`
  slot is how you get non-English reasoning out of the judge (`{"reason": "Die
  Antwort ist hilfreich und klar.", "pass": true, "score": 1.0}`).

### Claim 9: Test `vars` can be interpolated inside the LLM rubric text — e.g. quoting the `question` variable back at the grader to detect hallucinations — and objects in `{{output}}`/`{{rubric}}` are JSON-stringified by default unless `PROMPTFOO_DISABLE_OBJECT_STRINGIFY=true` enables property access
- **Evidence**: The "Using variables in the rubric" section (the
  `value: 'Says that it is uncertain or unable to answer the question: "{{question}}"'`
  hallucination example) and the "Object handling in variables" callout with
  the `{{output.text}}` pointer.
- **Confidence**: settled (documented product behavior)
- **Quote**: "You can use test `vars` in the LLM rubric. This example uses the `question` variable to help detect hallucinations:" and "When `{{output}}` or `{{rubric}}` contain objects, they are automatically converted to JSON strings by default to prevent display issues. To access object properties directly (e.g., `{{output.text}}`), enable object property access:"
- **Our assessment**: The vars-in-rubric mechanism is how hallucination rubrics
  become per-case rather than generic ("did the answer hedge on *this* question?")
  — and it proves the rubric is template-evaluated at eval time, which is the
  same surface a runtime-injected var can alter. The object-stringify default is
  a subtle correctness trap in the other direction: by default a rubric/
  output that is an object is stringified for grading, so a rubric authored
  against `{{output.text}}` silently grades the JSON string *unless* the env
  var flips the behavior — an env-dependent grader outcome in the same family
  as Claim 1.

### Claim 10: `llm-rubric` pass/fail is score-blind without a `threshold` — PASS depends only on the grader's `pass` field (defaulting to `true` when omitted), so a rubric that asks for a 0/1 score but omits `threshold` passes everything the judge doesn't explicitly flag
- **Evidence**: The "Understanding pass vs. score behavior" section's two
  mechanisms, the `{"pass": true, "score": 0}` example, and the "Common issue"
  troubleshooting block with its `# ❌ Problem: All tests pass regardless of score`
  config.
- **Confidence**: settled (documented product behavior, with a vendor-documented example)
- **Quote**: "Without threshold: PASS depends only on the grader's `pass` field (defaults to `true` if omitted)" and "With threshold: PASS requires both `pass === true` AND `score >= threshold`" and "This means a result like `{\"pass\": true, \"score\": 0}` will pass without a threshold, but fail with `threshold: 1`."
- **Our assessment**: The judge-tier twin of the hub note's `threshold: 0`
  silent-green footgun (#1287 Claim 3), but at the assertion level and
  score-blind: a rubric that returns scores without an explicit `pass: false`
  exhibits an all-pass default. The page's own troubleshooting framing calls it
  out directly. This is a must-have item in the "can your gate actually fail?"
  checklist: any `llm-rubric` without `threshold` is gated on the judge's
  goodwill to emit `pass: false`, which is exactly the judge-behavior risk
  #261's specific-rubric discipline is meant to remove.

### Claim 11: `agent-rubric` upgrades the rubric grader to a coding agent — it requires a coding-agent provider (default `openai:codex-sdk`, run isolated/read-only/no-approvals; alternatively Codex app-server, Claude Agent SDK, or OpenCode SDK), rejects plain-text providers, processes untrusted output/workspace content, and records `metadata.agentProvider`
- **Evidence**: The `agent-rubric` reference sub-page (followed per the
  triage's novel-capability flag): the definition, the default-provider
  sentence, the supported-provider table, the plain-text rejection note, the
  "Safety and side effects" section, and the results section.
- **Confidence**: settled (documented product behavior on the vendor's
  sub-page; the safety analysis is the page's own)
- **Quote**: "Without an explicit grading provider, `agent-rubric` uses `openai:codex-sdk` in an isolated temporary working directory with read-only sandboxing, no approvals, and structured JSON grading output:" and "A plain text provider such as `openai:responses:gpt-5` is rejected for `agent-rubric`. Use `llm-rubric` when the grader only needs the output and rubric text." and "An agentic grader processes untrusted target output and may read untrusted workspace content. The default grading prompt instructs it to treat that material as evidence rather than instructions, and the implicit Codex provider is read-only."
- **Our assessment**: Novel and operationally heavy. The judge is itself an
  agent that may run tools, so grading = running a second agent with its own
  sandbox policy; the page's own guidance is to keep workspaces read-only and
  confine any write/shell/network/MCP surface to disposable environments
  ("those actions are performed by the grader itself during the eval"). For the
  guide this is the strongest example yet that a model-graded gate can be
  *more* expensive and *more* privileged than the system under test — gating
  agent output by running an agent is the tool about to be loaded into CI, so
  its credential/execute power is itself attack surface. `metadata.agentProvider`
  is the provenance hook to at least record which agent runtime graded each row.

### Claim 12: `search-rubric` is an `llm-rubric` equivalent whose grader can do live web search — the judge's ability to verify current information is the point, and it carries a real per-call cost tier (roughly $10–45 per 1,000 search calls depending on provider) plus default-on caching that must be opted out of (`--no-cache`) for fresh searches
- **Evidence**: The `search-rubric` reference sub-page (followed per triage):
  the definition and "behaves exactly like `llm-rubric`" equivalence, the five
  web-search-capable grader options (Claude `web_search_20250305`, OpenAI
  `web_search_preview`, Perplexity `sonar`, Gemini `googleSearch`, xAI Grok
  Responses `web_search`), the "Cost Considerations" list ("As of November 2025"),
  and the Best Practices caching entry.
- **Confidence**: settled (documented cost tiers and behavior on the vendor
  sub-page; the cost figures are dated "as of November 2025")
- **Quote**: "The `search-rubric` assertion type is like `llm-rubric` but with web search capabilities. It evaluates outputs according to a rubric while having the ability to search for current information when needed." and "The `search-rubric` assertion behaves exactly like `llm-rubric`, but automatically uses a provider with web search capabilities:" and "Caching is enabled by default; use `promptfoo eval --no-cache` to force fresh searches"
- **Our assessment**: The page's cost list is the third-party-dependency tiering
  the triage asked to extract: a judge with live search is a per-verdict
  external spend (~$10–25/1k for OpenAI's Responses web-search tool calls,
  $35/1k Gemini grounded prompts, $45/1k Vertex Web Grounding, $25/1k xAI
  sources, plus tokens), which makes it the most expensive assertion family on
  the page — a direct counterpoint to the deterministic tier (#1289) that is
  free to rerun. The default-on caching is a doubled edge: it is the vendor's
  cost lever, but per the caching note (#1275 Claim 8 reasoning) a cached
  search verdict is stale, so *correctness* of a "current information" gate
  demands `--no-cache` while *cost* demands the opposite. The sub-page's own
  caveat ("The grader relies on web search results, which may occasionally be
  wrong or ambiguous") is the honest limit: the judge's ground truth is a live,
  mutable external corpus.

### Claim 13: Context-based RAG assertions (`context-recall`, `context-relevance`, `context-faithfulness`) are a special model-graded class that grades against context defined statically via `vars` or dynamically via `contextTransform`, which must return a non-empty string — with a documented null-fallback and a `JSON.stringify` debugging idiom
- **Evidence**: The "Context-based" section and the "Dynamically via Context
  Transform" subsection: the `ContextTransform` type signature, the
  `output.context ?? "No context found"` fallback, the
  `JSON.stringify(output, null, 2)` debug idiom, and the worked
  statically-defined example.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `contextTransform` property accepts a stringified Javascript expression which itself accepts two arguments: `output` and `context`, and **must return a non-empty string.**" and "If your expression should return `undefined` or `null`, for example because no context is available, add a fallback:" and "If you expected your context to be non-empty, but it's empty, you can debug your provider response by returning a stringified version of the response:"
- **Our assessment**: The empty-context question the triage flagged: the page
  does *not* document what `context-faithfulness` does against an empty /
  fallback context — it only mandates a non-empty string from `contextTransform`.
  That silence leaves the vacuous-pass question open: a fallback like `"No
  context found"` fed to a faithfulness judge tests nothing, and it will not be
  visible in the pass/fail report. Until a sibling reference answers it, Ch05
  should treat "context transform produced a fallback string" as an auditable
  condition rather than proof of grading. The `metadata`-accessible-on-the-
  second-arg detail (`context.metadata.retrieved_docs...`) is the RAG-data
  plumbing worth preserving in an artifact.

### Claim 14: The comparison types complete the model-graded gate: `select-best` picks a winner across prompts in one row by a criterion, and `max-score` aggregates other assertions' scores via `method`/`threshold` (worked gate: `method: average`, `threshold: 0.7`) — the aggregate-gate pattern that ties back to the hub's weighted-averaging model
- **Evidence**: The "Examples (comparison)" section: the `select-best`
  intro ("choose the funniest tweet") and the `max-score` example with
  `method: average` / `threshold: 0.7` under a `contains`+`llm-rubric` row.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The `select-best` assertion type is used to compare multiple outputs in the same TestCase row and select the one that best meets a specified criterion." and "The `max-score` assertion type is used to objectively select the output with the highest score from other assertions:"
- **Our assessment**: Opposite selections, one family: `select-best` starts from
  "there is a best," `max-score` starts from "there is an objectivity." The
  `max-score` gate is the model-graded compose point — it turns several
  per-assertion scores (including `llm-rubric`) into one pass/fail on their
  aggregate, which is the sub-page expression of the hub note's weighted-average
  model (#1287 Claims 1-2) as a single assert. Per Claim 5 the catch is that
  `select-best` "can read a scratchpad number as the winning index" on a
  self-hosted thinking judge — the comparison types are exposed to the same
  misparse surface.

## Concrete Artifacts

All artifacts copied character-for-character from
https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/
(sections as noted), except where a sub-page is cited.

### `llm-rubric` / `model-graded-closedqa` and `factuality` examples (verbatim from "Examples (output-based)")

```yaml
assert:
  - type: model-graded-closedqa # or llm-rubric
    # Make sure the LLM output adheres to this criteria:
    value: Is not apologetic
```

```yaml
assert:
  - type: factuality
    # Make sure the LLM output is consistent with this statement:
    value: Sacramento is the capital of California
```

### `trajectory:goal-success` configs (verbatim from "trajectory:goal-success")

```yaml
tests:
  - vars:
      order_id: '123'
    assert:
      - type: trajectory:goal-success
        value: 'Determine the shipping status for order {{ order_id }} and tell the user whether it has shipped'
```

```yaml
tests:
  - assert:
      - type: trajectory:goal-success
        value: Resolve the user's issue and provide the correct next step
        threshold: 0.8
        provider: openai:gpt-5.6
```

### Multilingual `rubricPrompt` (verbatim from "Non-English Evaluation")

```yaml
defaultTest:
  options:
    rubricPrompt: |
      [
        {
          "role": "system",
          // German: "You evaluate outputs based on criteria. Respond with JSON: {\"reason\": \"string\", \"pass\": boolean, \"score\": number}. ALL responses in German."
          "content": "Du bewertest Ausgaben nach Kriterien. Antworte mit JSON: {\"reason\": \"string\", \"pass\": boolean, \"score\": number}. ALLE Antworten auf Deutsch."
        },
        {
          "role": "user",
          // German: "Output: {{ output }}\nCriterion: {{ rubric }}"
          "content": "Ausgabe: {{ output }}\nKriterium: {{ rubric }}"
        }
      ]
assert:
  - type: llm-rubric
    # German: "Responds helpfully"
    value: 'Antwortet hilfreich'
```

Documented German reasoning output: `{"reason": "Die Antwort ist hilfreich und klar.", "pass": true, "score": 1.0}`

### Vars-in-rubric hallucination detection (verbatim from "Using variables in the rubric")

```yaml
providers:
  - openai:gpt-5.6
prompts:
  - file://prompt1.txt
  - file://prompt2.txt
defaultTest:
  assert:
    - type: llm-rubric
      value: 'Says that it is uncertain or unable to answer the question: "{{question}}"'
tests:
  - vars:
      question: What's the weather in New York?
  - vars:
      question: Who won the latest football match between the Giants and 49ers?
```

### Grader override precedence forms (verbatim from "Overriding the LLM grader")

```bash
promptfoo eval --grader openai:gpt-5.6
```

```yaml
defaultTest:
  options:
    provider: openai:gpt-5.6
tests:
  - description: Use LLM to evaluate output
    assert:
      - type: llm-rubric
        value: Is spoken like a pirate
```

```yaml
tests:
  - description: Use LLM to evaluate output
    assert:
      - type: llm-rubric
        value: Is spoken like a pirate
        provider: openai:gpt-5.6
```

`provider.config` for custom judge parameters:

```yaml
tests:
  - assert:
      - type: llm-rubric
        value: Is not apologetic and provides a clear, concise answer
        provider:
          id: openai:gpt-5.6
          config:
            temperature: 0
```

### Self-hosted thinking judge config (verbatim from "OpenAI-compatible thinking judges")

```yaml
defaultTest:
  options:
    provider:
      id: openai:chat:llm_judge
      config:
        apiBaseUrl: http://localhost:8000/v1
        apiKey: empty
        temperature: 0
        max_tokens: 10000
        showThinking: false
```

### `max-score` aggregate gate (verbatim from "Examples (comparison)")

```yaml
prompts:
  - 'Write a summary of {{article}}'
  - 'Write a detailed summary of {{article}}'
  - 'Write a comprehensive summary of {{article}} with key points'
providers:
  - openai:gpt-5.6
tests:
  - vars:
      article: 'AI safety research is accelerating...'
    assert:
      - type: contains
        value: 'AI safety'
      - type: contains
        value: 'research'
      - type: llm-rubric
        value: 'Summary captures the main points accurately'
      - type: max-score
        value:
          method: average # Use average of all assertion scores
          threshold: 0.7 # Require at least 70% score to pass
```

### contextTransform fallback and debug idioms (verbatim from "Dynamically via Context Transform")

```yaml
contextTransform: 'output.context ?? "No context found"'
```

```yaml
contextTransform: 'JSON.stringify(output, null, 2)'
```

### The vendor's "always pass" example rubric (verbatim from "Overriding the rubric prompt")

```yaml
defaultTest:
  options:
    rubricPrompt: >
      [
        {
          "role": "system",
          "content": "Grade the output by the following specifications, keeping track of the points scored:\n\nDid the output mention {{x}}? +1 point\nDid the output describe {{y}}? +1 point\nDid the output ask to clarify {{z}}? +1 point\n\nCalculate the score but always pass the test. Output your response in the following JSON format:\n{pass: true, score: number, reason: string}"
        },
        {
          "role": "user",
          "content": "Output: {{ output }}"
        }
      ]
```

### `agent-rubric` graded-by-agent config (verbatim from the `agent-rubric` sub-page)

```yaml
tests:
  - assert:
      - type: agent-rubric
        value: Verify that the output accurately describes the exported API in src/report.ts.
        provider:
          id: openai:codex-sdk
          config:
            working_dir: ./sample-project
            sandbox_mode: read-only
            approval_policy: never
            skip_git_repo_check: true
```

Instantiation note from the same sub-page: the documented default grader is
"an isolated temporary working directory with read-only sandboxing, no
approvals" via `openai:codex-sdk`, with Claude Agent SDK / Codex app-server /
OpenCode SDK as alternatives.

### Objects-in-template behavior (verbatim from "Object handling in variables")

```bash
export PROMPTFOO_DISABLE_OBJECT_STRINGIFY=true
promptfoo eval
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 11** (the hub
    page's catalogue row for `trajectory:goal-success`: "Use an LLM judge to
    decide whether the traced agent run achieved its goal", with a
    judge-variance caveat inherited from #261) — this page supplies the
    judge-layer mechanics under that row (trace requirement, summarize-then-judge
    flow, `not-` inversion, grader overrides). (Verified: #1287 Claim 11.)
  - `source-notes/docs-promptfoo-classifier-grading.md` **Claim 9** (the
    classifier note's own guidance that "model-graded evals are also a good
    choice... especially if you want to quickly tune the eval to your use
    case") — this page *is* that tier in full: the model-graded family and its
    `rubricPrompt` tunability substantiate the "quickly tune" positioning from
    the fixed-classifier rung. (Verified: #1288 Claim 9.)
  - `source-notes/blog-promptfoo-asr-not-portable-metric.md` **Claim 8** (two
    judges with equal 80% accuracy can show a 14-point ASR gap from differing
    TPR/FPR splits) **and Claim 11** (specific rubrics make different judge
    models converge; vague rubrics leave interpretation to the judge) — the
    mechanism surface this page documents (ambient judge selection, Claim 1;
    custom `rubricPrompt`, Claims 8/14; score-blind pass, Claim 10) is exactly
    where that measured judge variance operates. The page corroborates the risk
    frame from the config side; #261 supplies the empirical reason it matters.
    (Verified: #261 Claim 8 = 14-pp TPR/FPR example; Claim 11 = specific-rubric
    convergence.)

- **Contradicts**: None identified, and no new contradiction issue filed.
  Checked `CONTRADICTIONS.md` (no open `C-NNN` entries) and open
  `contradiction`-labeled issues: #1150 (unrelated LiteLLM routing) and #1307
  (promptfoo missing-trace semantics). **#1307 is related context, not a
  conflict with this page**: it pits the built-in trace family *throwing*
  "could not be evaluated" when trace data is absent (#1289 Claim 12) against
  the custom-JS `if (!context.trace) return true` silent-pass guard (#1304).
  This page's `not-` inversion fail-closed claim (Claim 4) sits on the same
  *fail-closed* side of that axis as the built-in family and opposes no existing
  claim. Also checked: the hub note's `threshold: 0` / `weight: 0` silent-green
  footguns (#1287 Claims 3/4) are config-level; this page's fail-closed inversion
  is judge-transport-level, so they are complementary mechanisms, not competing
  claims. No contradiction issue warranted.

- **Extends**:
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) — directly
    closes that note's explicitly-open thread. Its Extraction Notes ends "the
    residual unpinned inputs are the judge models behind model-graded
    assertions"; this page answers *how* they are unpinned (ambient credential
    selection, Claims 1-2) and adds the judge-tier failure semantics
    (pass-vs-score, Claims 10; reasoning-misparse, Claims 5-6) underneath the
    hub's aggregation/scoring model. Also extends #1287 Claim 10's
    deterministic-vs-model-assisted boundary with the model-graded side in full.
    (Verified: #1287 Claim 10 boundaries; the residual-judge statement is in
    #1287's Extraction Notes.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 1** (the
    vendor-drawn boundary excluding `classifier`, `pi`, `select-best`,
    `similar` as "use an additional model or external inference service") —
    this page is the deep-dive on the *model-graded* side of that boundary that
    #1289 deliberately excluded; the two notes are the pinned-judge
    (deterministic, free to rerun) vs ambient-judge (model-graded, per-verdict
    cost) contrast the triage positioned. (Verified: #1289 Claim 1.)
  - `source-notes/blog-promptfoo-red-team-claude.md` **Claim 10** (custom
    red-team test cases use an `llm-rubric` grader, e.g. `'Must include
    appropriate disclaimers'`, without documenting its grading semantics) —
    this page supplies those semantics: `threshold` behavior (Claim 10), the
    `rubricPrompt` override surface (Claims 8-9), and the judge-pinning
    requirement (Claims 1-2) that a red-team config carrying `llm-rubric` should
    honor. (Verified: #690/#482 Issue reference — read Claim 10 of the Claude
    red-team note directly.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8**
    (per-repeat cache namespaces; `--no-cache` + `--repeat` needed for fresh
    runs) — this page's `search-rubric` fresh-search requirement ("use
    `promptfoo eval --no-cache` to force fresh searches", Claim 12) and the
    judge-tier default-on caching extend the caching note's reproducibility
    thesis from fresh-run methodology to the web-search grader tier.
    (Verified: #1275 Claim 8.)

- **Novel**: First corpus coverage of the **model-graded (LLM-judge) assertion
  tier** as a config surface — the sibling notes covered aggregation (#1287),
  the classifier rung (#1288), and the deterministic tier (#1289), but none
  documented the judge itself:
  1. **Ambient grader selection** (Claim 1) — the judge model is a function of
     whatever credentials are in the environment; the config does not pin it.
  2. **The grader-override precedence chain and the shorthand-provider
     `config`-inheritance trap** (Claim 2) — an assertion-level `provider:` can
     silently disable the global provider object's `apiBaseUrl`/`apiKey`/
     `temperature`/`showThinking`.
  3. **The `not-` fail-closed inversion** (Claim 4) — documented for the
     inverted trajectory form only; the asymmetry is itself a finding.
  4. **Judge reasoning leakage** (Claims 5-6) — `showThinking: false` and the
     cross-family scratchpad-misparse surface; the vLLM unfinished-`thinking`
     block caveat. A silent-misgrade (wrong verdict, not error) failure class.
  5. **Judge determinism knobs** (Claim 7) — built-in `temperature=0`; GPT-5
     reasoning models ignore `temperature`.
  6. **`agent-rubric` and `search-rubric`** (Claims 11-12) — the judge is
     itself an agent (with workspace/tool sandboxing consequences) or a
     web-search caller (with per-call cost tiers).
  7. **Score-blind pass semantics** (Claim 10) — `llm-rubric` without
     `threshold` passes on the judge's `pass` field defaulting to `true`.
  8. **The empty-context silence** (Claim 13) — `contextTransform` must return
     non-empty, but the page does not state what a faithfulness judge does with
     a fallback string (vacuous-pass question left open).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology**:
  Add the **judge-pinning rule** to the gate-review checklist (extending the
  evaluator-trust material the classifier note ties to #261): (a) the judge
  behind every model-graded assert is ambient by default (Claim 1) — pin it via
  `--grader`, `defaultTest.options.provider`, or `assertion.provider`, and
  account for the fact that an assertion-level shorthand silently drops the
  global provider's `config` (Claim 2); (b) audit `llm-rubric` asserts for the
  score-blind pass default — no `threshold` means a judge that omits `pass:
  false` passes regardless of score (Claim 10), the judge-tier twin of the hub
  config traps; (c) for self-hosted judges require `showThinking: false` and
  size `max_tokens`/context so reasoning cannot leak into the graded string
  (Claims 5-6); (d) do not rely on `temperature=0` for GPT-5-series judges — it
  is ignored (Claim 7). Where `guide/05-llm-ops-reliability.md` already states
  the hermetic-replay rule (#1287/#1275), extend it to the judge layer: a gate
  whose judge is ambient and whose web-search grader reads a live corpus (Claim
  12) is non-hermetic by construction.
- **Chapter 05 — cost tiering**: state the cost ladder for gates: deterministic
  asserts are free to rerun (#1289); model-graded asserts consume an extra
  inference call per verdict; `search-rubric` adds per-call web-search fees
  (~$10-45 per 1,000 calls, Claim 12); `agent-rubric` runs a full coding agent
  per check (Claim 11). This gives the "use the cheapest tier that can verify
  the property" rule concrete numbers.
- **Chapter 06 (Security and Trust) — judge trust / red-team gates**: record
  the fail-closed inversion semantics (Claim 4): a `not-trajectory:goal-success`
  gate cannot be silently passed by a broken judge — but label it explicitly as
  vendor-documented for the inverted form only, so the guide does not overclaim
  a general fail-closed law. Add the "judge can be told to lie" caution from the
  vendor's own `"Calculate the score but always pass the test"` example rubric
  (Concrete Artifacts) — copy-pasting doc rubrics into a red-team gate inherits
  whatever the example says, including an instruction to pass.
- **Chapter 03 (Runbooks and Agents) — agent-goal grading**: add
  `trajectory:goal-success` (Claim 3) as the goal-attainment gate beside the
  deterministic trajectory checks (`trajectory:tool-used` / `:tool-sequence`
  from #1289), with the trace-data dependency noted — the assertion requires
  trace data and is judged by an LLM, so the gate couples to both the tracing
  pipeline and an ambient judge (pin it). Document `agent-rubric` (Claim 11) as
  the "verify a claimed change against the workspace" grader with its sandbox
  caveats: the grader runs a coding agent inside the eval, so read-only
  workspaces and disposable environments are the safe posture; everything the
  grader can do (shell, network, MCP, app connectors) is executed during the
  eval.
- **Chapter 02 (Observability) — trace-asserted gates**: state that model-graded
  trajectory assertions consume the same OTel-shaped trace data the deterministic
  family consumes (#1289 Claim 12's throw-when-absent behavior), and that a
  judge transport failure under `not-` reports as a failure (Claim 4) — the
  missing-trace and broken-judge failure semantics should be cross-referenced
  with the open contradiction #1307 so Ch02's "what does a red eval run mean"
  guidance distinguishes infra-red (trace absent / judge error) from
  model-red.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/configuration/expected-outputs/model-graded/).
  "Last updated on Sep 14, 2026" — page undated, so `date_published` carries
  the last-updated date (same convention as the sibling notes). Quotes verified
  character-for-character against the fetched rendered content before writing;
  code blocks copied verbatim.
- **Sub-pages followed (2 of the page's sub-page family, per the triage's
  novel-capability flag)**: `agent-rubric` and `search-rubric`. Their config
  semantics feed Claims 11-12 and the two artifacts; all sub-page quotes verified
  against those fetches. The remaining sub-pages (g-eval, pi, llm-rubric,
  model-graded-closedqa, factuality, answer-relevance, conversation-relevance,
  context-recall/relevance/faithfulness, max-score, select-best) were NOT
  followed — they are per-type reference pages, consistent with the sibling
  extraction convention (#1287/#1288/#1289 each treated sub-pages as separate
  surfaces), and their names/one-liners are catalogued on this page without
  claim-level depth.
- **Triage key-question resolution**: the fail-closed behavior
  ("judge transport or parse failures still report as failures") is documented
  for the inverted `not-trajectory:goal-success` form *only* — the page states
  no general property for all model-graded assertions, and the positive
  `trajectory:goal-success` path carries no analogous sentence. Recorded as the
  asymmetry finding in Claim 4 rather than asserted as a general law.
- **Empty-context finding**: the page mandates a non-empty return from
  `contextTransform` but does not state what `context-faithfulness` does with an
  empty or fallback context — left open in Claim 13 rather than invented.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by name):
  - `docs-promptfoo-classifier-grading.md` — **cited** (Corroborates, Claim 9).
  - `docs-promptfoo-assertions-metrics.md` — **cited heavily** (Corroborates/
    Extends, Claims 10/11 + the residual-judge Extraction Notes statement).
  - `blog-promptfoo-red-team-claude.md` — **cited** (Extends, Claim 10).
  - `blog-promptfoo-owasp-red-teaming.md` — OWASP red-team methodology/SDLC
    phases (Claim 4 touches CI/CD integration); no model-graded-tier semantics;
    dismissed.
  - `blog-promptfoo-red-team-gemini.md` — per-model red-team plugin strategy and
    reasoning-DoS testing; uses a rubric/latency assert as a tool but carries no
    judge-grading semantics from this page's family; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — AI-incident triage by an SRE Agent
    using LLM-as-judge *alerts*; no eval-assert config surface; dismissed.
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-reliable-product-launches.md`
    — Google SRE book/workbook chapters (team org, launch process); no LLM-eval
    content; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `docs-promptfoo-javascript-assertions.md` (#1304 sibling) — custom-JS
    assertion surface with the `context.trace` silent-pass guard at the heart of
    open contradiction #1307; no model-graded-judge semantics, so dismissed as a
    cross-ref (but noted as the #1307 Side A).
  - Two cross-refs (`docs-promptfoo-deterministic-metrics.md` #1289,
    `docs-promptfoo-configuration-caching.md` #1275) plus
    `blog-promptfoo-asr-not-portable-metric.md` (#261) overlap-listed in the
    triage and found in `source-notes/` per MINER.md §4.
- **Cross-ref verification (§4b)**: every cited claim was located in the cited
  note before writing — #1287 Claims 10/11, #1288 Claim 9, #1289 Claim 1,
  #261 Claims 8/11, #1275 Claim 8, and `blog-promptfoo-red-team-claude.md`
  Claim 10 were all read and confirmed; claims cited for corroboration
  (trajectory catalogue row, deterministic boundary, judge-variance examples)
  match their one-line content in the cited notes. No claim numbers invented.
- **No contradiction issue filed**: the page opposes no existing source-note
  claim (verified against `CONTRADICTIONS.md` and open `contradiction`-labeled
  issues). The adjacent open contradiction #1307 (missing-trace semantics) is
  cross-surface context, not opposition: this page's fail-closed inversion
  aligns with the built-in trace family's fail-loud side. The closest surfaces
  (hub `threshold: 0`/`weight: 0`, classifier-trust caveats) are complementary
  mechanisms.
- `confidence_overall` is `emerging`, matching the sibling promptfoo config
  notes (#1287, #1288, #1289): individual mechanism/default claims are
  settled-for-product-behavior and directly checkable against an installed CLI,
  but this is vendor documentation with no measured gate-failure, judge-
  agreement, or cost figures and no independent practitioner validation — the
  operational-consequence framing (jugde non-hermeticity, silent misgrade,
  vacuous-context questions) is the Miner's synthesis on top of documented
  behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited;
  they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.