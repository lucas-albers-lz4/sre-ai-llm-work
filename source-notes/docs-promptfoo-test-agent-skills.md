---
source_url: https://www.promptfoo.dev/docs/guides/test-agent-skills
source_type: docs
title: "Promptfoo Guide: Test Agent Skills — Skill-Version A/B Testing, Routing-Boundary Checks, and the Per-Provider Evidence Ladder"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-19
date_extracted: 2026-10-20
last_checked: 2026-10-20
status: current
confidence_overall: emerging
issue: "#1799"
---

# Promptfoo Guide: Test Agent Skills

> A vendor recipe for regression-testing a *skill version* rather than an
> agent's output text: hold model, task fixtures, and permissions constant and
> swap only `SKILL.md`; assert routing with `skill-used` (and `not-skill-used`
> for near-miss prompts in bundles), score outcome quality with a recall
> assertion, then layer cost/latency/`max-score` as secondary signals — with
> the same eval runnable against Claude Agent SDK, Codex SDK, and OpenCode SDK,
> each with different evidentiary strength for the same assertion.

## Source Context

- **Type**: docs (vendor guide page — promptfoo `/docs/guides/`,
  Evaluation Techniques section; page footer "Last updated on Oct 19, 2026 by
  Michael D'Angelo")
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation with runnable configs (`skill-comparison` example
  repos for both Claude and Codex), so the assertion mechanics and config flags
  are directly checkable against an installed CLI. Vendor-positioned on
  efficacy: the page reports **no pass-rate, flake-rate, or before/after
  measurements** for any skill version, so the protocol itself is the claim,
  not evidence that per-version evals improve skills.
- **Scope**: The skill-scoped evaluation layer — A/B skill-version comparison,
  routing assertions, per-provider skill-invocation evidence, structured-output
  forcing, and bundle routing boundaries. It does NOT re-derive the assertion
  catalogue (`skill-used` semantics, `max-score` weighting math,
  `cost`/`latency` assertion behavior, `disableVarExpansion` mechanics) — each
  is owned by sibling reference-page notes and is cited, not extracted, here.

## Extracted Claims

### Claim 1: A skill version is evalable by holding everything constant and swapping only the `SKILL.md` — one fixture directory per version, providers differing only in `working_dir`
- **Evidence**: Complete `promptfooconfig.yaml` with two
  `anthropic:claude-agent-sdk` provider entries whose configs are identical
  except `working_dir: ./fixtures/v1` vs `./fixtures/v2`; each fixture holds
  the same `src/auth.ts` source file and a different copy of
  `.claude/skills/review-standards/SKILL.md`. YAML anchor `&reviewSchema`
  shares one output schema across both providers.
- **Confidence**: emerging (documented, runnable methodology; no measured
  skill-quality outcomes)
- **Quote**: "Keep the model, task files, and permissions the same, swap only the `SKILL.md`, and compare the results." and "Because everything else is held constant, any meaningful difference in the results should come from the skill text itself."
- **Our assessment**: Buy it as an eval-design rule — it is the controlled-
  experiment form of "the skill text is the independent variable," and it is
  the concrete procedure the corpus lacked (existing notes define what a
  SKILL.md *is* and assert *that* a skill routed, but never how to attribute a
  behavioral delta to a skill *edit*). The attribution claim is only as strong
  as the constant-holding: model, permissions, task files, and prompt must all
  be pinned, and nondeterminism still requires repeats (Claim 11).

### Claim 2: `skill-used` is capability attribution, not just routing — it separates a good answer made through the intended skill from one produced incidentally
- **Evidence**: The stated purpose of the first assertion layer, immediately
  after the `skill-used` config block; Claude's `Skill` tool calls are
  normalized by Promptfoo into the assertion.
- **Confidence**: emerging (eval-design rule; the assertion's mechanics are
  settled, the reframing is the vendor's)
- **Quote**: "This distinguishes a good answer that happened without the skill from one that was produced through the workflow you intended to test."
- **Our assessment**: This is the highest-value reframe in the page. Existing
  corpus notes treat `skill-used` as a trace/routing check inside the
  telemetry family (`docs-promptfoo-assertions-metrics.md` Claim 11,
  `docs-promptfoo-deterministic-metrics.md` Claim 3); this page turns it into
  an *eval-validity precondition* — without it, an outcome-quality score may be
  measuring the model's unaided competence, not the skill under test. That is
  the difference between "the skill works" and "the answer was good."

### Claim 3: A bundle eval needs three layers — positive prompts, near-miss prompts asserting both `skill-used` and `not-skill-used`, and output checks proving the chosen skill changed the work
- **Evidence**: A "Test Routing Boundaries In Bundles" section with two
  mirrored test cases (eval-authoring prompt asserting
  `skill-used: promptfoo-evals` + `not-skill-used: promptfoo-provider-setup`,
  and the inverse), then an explicit three-layer list.
- **Confidence**: emerging (documented methodology; no measured
  boundary-detection rates)
- **Quote**: "For a bundle, do not test only the happy-path prompt for each skill. Add nearby prompts that should route to a sibling instead, then assert both the skill you want and the skills you do not want:" followed by the page's list: "1. Positive prompts that should trigger each skill. 2. Near-miss prompts that should trigger a sibling instead. 3. Output checks that prove the chosen skill changed the work, not just the routing trace."
- **Our assessment**: The most novel pattern on the page. Layer 2 is an
  over-trigger test — the failure mode where a skill's description is too
  broad and swallows sibling traffic — and layer 3 prevents a green route
  trace from standing in for actual work quality (Claim 2's rule applied to
  the bundle). For the guide this is a test-design template: name the
  neighboring skill, write the near-miss prompt, assert both directions.
  `not-skill-used` itself is a documented primitive
  (`docs-promptfoo-deterministic-metrics.md` Claim 3) — what is new is the
  bundle-boundary use of it.

### Claim 4: The same `skill-used` assertion carries different evidentiary strength per provider — first-class tool call (Claude, OpenCode) vs inferred file-read (Codex)
- **Evidence**: Three provider sections spelling out the mechanism: Claude
  exposes `Skill` tool calls directly; OpenCode normalizes its native `skill`
  tool; Codex has no skill event at all and Promptfoo infers the signal from
  successful reads of the matching `SKILL.md`, which requires streaming to be
  on.
- **Confidence**: settled (documented product behavior — checkable against
  each installed SDK)
- **Quote**: "For Claude Agent SDK and OpenCode SDK, `skill-used` is usually enough to prove invocation because it is based on first-class skill tool calls." and "Its `skill-used` signal is inferred from successful reads of the matching `SKILL.md`, so keep `enable_streaming: true` while developing the eval if you want Promptfoo to collect that evidence." and "OpenCode discovers `.agents/skills/` directories in the working-directory hierarchy, then loads the matching skill through its native `skill` tool."
- **Our assessment**: Real footgun, buy it. The assertion name is identical
  across providers but the proof differs: an observed tool invocation vs a
  successful file read (which could occur without the skill being *applied*).
  Codex's variant additionally fails *silently* without
  `enable_streaming: true` — the eval still runs, the evidence just isn't
  collected. This extends
  `docs-promptfoo-evaluate-openai-agents-python.md` Claim 10 (Python SDK has
  no first-class skill event either, and the guidance there is to assert the
  observable workflow) into a per-provider evidence ladder: first-class call >
  native-tool normalization > inferred file-read > workflow proxy.

### Claim 5: Claude's `skills:` filter is version-gated — added in `@anthropic-ai/claude-agent-sdk` 0.2.120, it narrows the session to one skill and auto-allows the `Skill` tool; older SDKs must list `Skill` in `append_allowed_tools`
- **Evidence**: The paragraph under the Claude provider config, plus
  `setting_sources: ['project']` for `.claude/skills/` discovery and the
  `skills: 'all'` alternative.
- **Confidence**: settled (documented product behavior with an exact version
  number)
- **Quote**: "The `skills:` filter (added in `@anthropic-ai/claude-agent-sdk` 0.2.120) narrows the session to a single skill and auto-allows the `Skill` tool, so it no longer needs to appear in `append_allowed_tools`." and "On older SDK versions, drop `skills:` and add `'Skill'` back to `append_allowed_tools`." and "`setting_sources: ['project']` discovers `SKILL.md` files under `.claude/skills/`."
- **Our assessment**: Version-gated config is exactly the class of detail that
  makes a "it works on my machine" eval — an older SDK silently loses both the
  skill filter and the auto-allow, so the session may not invoke `Skill` at
  all, and the routing assertion fails (or worse, the skill never loads and
  the outcome score quietly measures the bare model). Pin the SDK version
  alongside the pinned model when reproducing this recipe.

### Claim 6: Structured output is forced per provider, not in the prompt — Claude `output_format`, Codex `output_schema` (keeps output a JSON *string*), OpenCode `format.type: json_schema`, shared via one YAML anchor
- **Evidence**: The `x-review-schema` anchor defined twice with provider-appropriate
  shapes (Claude's `type: json_schema` wrapper vs Codex's bare schema object),
  applied in all three provider blocks; a code comment explains why.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The Claude Agent SDK's `output_format` is the equivalent of Codex's `output_schema` — it returns valid JSON without you having to ask for \"JSON only\" in the prompt or strip Markdown fences from the model's reply." and "The earlier JavaScript assertion should use `JSON.parse(output)` with Codex because `output_schema` keeps `output` as a JSON string rather than a parsed object."
- **Our assessment**: Corroborates
  `docs-promptfoo-evaluate-coding-agents.md` Claim 12 (provider-enforced
  structured output is the recommended first eval shape) and explains the
  output-shape divergence that `docs-promptfoo-javascript-assertions.md`
  Claim 4 flags as a within-page conflict: the string-vs-object behavior is
  provider-dependent, and the page's shared assertion defensively does
  `typeof output === 'string' ? JSON.parse(output) : output`. Reusable
  pattern: one schema anchor, three provider dialects, so the scoring
  assertion doesn't fight Markdown fences.

### Claim 7: Outcome quality is scored as issue recall in a JavaScript assertion — expected issue IDs in vars, recall ≥ 0.75 passes, `threshold: 0.7`
- **Evidence**: A full `javascript` assertion computing
  `hits.length / expected.length` over `context.vars.expectedIssues`, with
  `pass: recall >= 0.75`, `score: recall`, and a reason string reporting
  matched/expected counts; the assertion block carries `threshold: 0.7`.
- **Confidence**: settled (the assertion contract is documented product
  behavior; the specific recall metric is an example, not a default)
- **Quote**: "The JavaScript assertion gives each response a score based on issue recall." and "In your own eval, replace this with the signal that matters for the skill: tests passed, required edits were made, policy checks were followed, or a rubric was satisfied."
- **Our assessment**: The recall assertion is the *outcome* half of the
  two-signal design (routing per Claim 2 + quality here). Note the metric
  contract of `javascript` assertions per
  `docs-promptfoo-javascript-assertions.md` Claim 1 — the returned
  `{pass, score, reason}` shape and fail-closed-on-throw behavior (Claim 2
  there) apply; a malformed output would throw in `JSON.parse` and hard-fail
  the case, which is why Claim 6's provider-enforced schema matters. The
  vendor explicitly invites swapping in domain signals, so the recall metric
  is a template, not doctrine.

### Claim 8: Broad and narrow task fixtures are paired deliberately so the eval rewards scope-respect, not just issue-finding
- **Evidence**: Two test cases over the same `src/auth.ts` — one requesting
  both password-handling and token-comparison review with two expected issues,
  one requesting only password handling with a single expected issue — with an
  explanatory paragraph.
- **Confidence**: emerging (eval-design rationale; no data that the pairing
  catches the failure mode in practice)
- **Quote**: "Pairing the two together is what lets the eval reward a skill version that both knows the full set of issues *and* respects the user's scope when asked."
- **Our assessment**: Buy it — a skill that always dumps every known issue
  fails the narrow case, and one that is timid fails the broad case; the pair
  makes both failure modes visible in one run. This is fixture design, not
  assertion config, and it generalizes beyond review skills: every skill eval
  should include a prompt that deliberately under-scopes the request.

### Claim 9: `disableVarExpansion: true` is required in comparison tests or YAML-list vars fan out into separate cases and break `expectedIssues`
- **Evidence**: `defaultTest.options.disableVarExpansion: true` set in the
  tests block, with a code comment naming the failure mode; links to the
  "Passing Arrays to Assertions" doc.
- **Confidence**: settled (documented product behavior; mechanics owned by
  `docs-promptfoo-configuration-guide.md` Claim 12)
- **Quote**: "By default, Promptfoo fans each YAML-list var into one test case per element (matrix expansion), which would split each comparison test in two. Disable that here so `expectedIssues` reaches the assertion intact."
- **Our assessment**: Cited, not re-derived — the cartesian-expansion
  semantics and the `defaultTest.options` placement of the escape hatch are
  already owned by `docs-promptfoo-configuration-guide.md` Claim 12. What is
  new here is the failure *consequence in this pattern*: the array silently
  becomes two test cases, the assertion's `expectedIssues` arrives fanned-out,
  and the recall scorer grades the wrong fixture. Per the Prospector's scope
  guidance, the mechanics were skipped and only the reliance recorded.

### Claim 10: Cost and latency are secondary gates, optionally aggregated by `max-score` with type-keyed weights, so a correct-but-slower skill version does not win by default
- **Evidence**: `cost: threshold 0.50` and `latency: threshold 120000`
  assertions, plus a `max-score` block with `method: average`,
  `threshold: 0.7`, and `weights: {javascript: 4, skill-used: 2, cost: 0.5,
  latency: 0.5}`.
- **Confidence**: settled (documented product behavior; weighting semantics
  owned by `docs-promptfoo-max-score.md`)
- **Quote**: "These checks are useful when two skill versions are both correct but one is much more expensive or slower." and "That weighting makes task quality the main signal, while still rewarding the version that routes correctly and stays within practical limits."
- **Our assessment**: The layering order is the guidance — correctness first,
  budget second, never a budget assertion standing alone as the quality gate.
  Mechanically consistent with `docs-promptfoo-max-score.md` Claim 4 (weights
  are keyed by assertion *type*, so `javascript: 4` weights every JS assertion
  in the row, not "the recall one") — worth remembering before editing the
  weights. No measured cost/latency figures for any skill version appear on
  the page; the thresholds are illustrative.

### Claim 11: Winner selection requires repeats and cache-off runs — skill selection is nondeterministic, so a single lucky run does not pick the better skill
- **Evidence**: CLI guidance block with `--repeat 3`, `--no-cache`,
  `-o results.json`, and `npx promptfoo@latest view`, plus the closing
  decision rule.
- **Confidence**: emerging (methodology; the vendor reports no flake rates to
  quantify *how much* repetition is enough)
- **Quote**: "Add `--repeat 3` when you want a better sample of nondeterministic agent behavior." and "Add `--no-cache` while iterating on the skill text and you want fresh runs." and "The better skill is the one that holds up across the tasks you care about, not the one that wins a single lucky run."
- **Our assessment**: Corroborates
  `docs-promptfoo-evaluate-coding-agents.md` Claim 10 (regression gates are
  cost/latency thresholds plus `--no-cache` and `--repeat 3`) and the
  `--no-cache`-for-fresh-cost rule in
  `docs-promptfoo-deterministic-metrics.md` Claim 6. The open question the
  page does not answer: `--repeat 3` is asserted, not derived — three runs of
  a nondeterministic router is a thin sample, and the vendor publishes no
  variance data to justify it. Treat 3 as a floor for iteration, not a
  statistical guarantee.

### Claim 12: Codex routing evidence can be backed by trajectory traces — `deep_tracing: true` plus a `trajectory:step-count` assertion pattern-matching `*review-standards/SKILL.md*`
- **Evidence**: A `deep_tracing`/`tracing.enabled` provider config and an
  assertion requiring ≥1 command step whose pattern matches the skill file
  path; the page notes Codex app-server for app-server-specific skill behavior.
- **Confidence**: settled (documented product behavior — pattern match against
  a trajectory step)
- **Quote**: "For Codex SDK, trace evidence can be useful when you want to see the workflow behind the final answer."
- **Our assessment**: The fallback leg of Claim 4's evidence ladder: when the
  inferred `skill-used` (file read) is too weak, assert the trace directly.
  Note the interaction with `docs-promptfoo-deterministic-metrics.md` Claim
  12 — the trace/trajectory family *throws* when trace data is unavailable, so
  this leg inherits an observability dependency (`enable_streaming` /
  `deep_tracing` must be on or the gate errors rather than fails green).
  Chain of evidence for Codex: `skill-used` inference → `trajectory:step-count`
  SKILL.md read → raw `javascript` over recorded tool calls (the Claude
  `toolCalls` inspection shown in the same section).

## Concrete Artifacts

Fixture layout for a two-version skill comparison (source: promptfoo
`test-agent-skills` guide, "Start With One Comparison"; line breaks restored
at tree boundaries from the rendered page):

```
skill-eval/
├── promptfooconfig.yaml
└── fixtures/
    ├── v1/
    │   ├── .claude/skills/review-standards/SKILL.md
    │   └── src/auth.ts
    └── v2/
        ├── .claude/skills/review-standards/SKILL.md
        └── src/auth.ts
```

Routing-boundary bundle tests (source: promptfoo `test-agent-skills` guide,
"Test Routing Boundaries In Bundles"):

```yaml
tests:
  - description: Eval authoring stays out of provider setup
    vars:
      request: Write a regression eval for this existing provider.
    assert:
      - type: skill-used
        value: promptfoo-evals
      - type: not-skill-used
        value: promptfoo-provider-setup
  - description: Provider wiring does not become eval authoring
    vars:
      request: Connect this HTTP endpoint and verify one safe smoke call.
    assert:
      - type: skill-used
        value: promptfoo-provider-setup
      - type: not-skill-used
        value: promptfoo-evals
```

Issue-recall JavaScript assertion (source: promptfoo `test-agent-skills`
guide, "Score the Output"):

```yaml
defaultTest:
  assert:
    - type: javascript
      threshold: 0.7
      value: |
        const result = typeof output === 'string' ? JSON.parse(output) : output;
        const expected = context.vars.expectedIssues;
        const found = (result.issues || []).map((issue) => issue.id);
        const hits = expected.filter((id) => found.includes(id));
        const recall = hits.length / expected.length;
        return {
          pass: recall >= 0.75,
          score: recall,
          reason: `matched ${hits.length}/${expected.length} expected issues`,
        };
```

Codex routing + trace evidence (source: promptfoo `test-agent-skills` guide,
"Use the Same Eval With Codex" / "Add Trace Evidence When Needed"):

```yaml
providers:
  - id: openai:codex-sdk
    label: review-standards-v1
    config:
      model: gpt-5.5
      working_dir: ./fixtures/v1
      skip_git_repo_check: true
      sandbox_mode: read-only
      enable_streaming: true
      output_schema: *reviewSchema
      deep_tracing: true
tracing:
  enabled: true
tests:
  - assert:
      - type: trajectory:step-count
        value:
          type: command
          pattern: '*review-standards/SKILL.md*'
          min: 1
```

`max-score` weighting for secondary signals (source: promptfoo
`test-agent-skills` guide, "Add Secondary Signals"):

```yaml
defaultTest:
  assert:
    - type: max-score
      value:
        method: average
        threshold: 0.7
        weights:
          javascript: 4
          skill-used: 2
          cost: 0.5
          latency: 0.5
```

Runnable examples named by the page: `examples/openai-codex-sdk/skill-comparison`
and `examples/claude-agent-sdk/skill-comparison` in the promptfoo GitHub repo.

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` — Claim 3 (the
    `not-` negation family, whose Our-assessment explicitly names
    `not-skill-used` as the forbidden-skill gate) and the trace/trajectory
    family scope; this page's bundle tests (Claim 3 above) are the
    application of that primitive to skill routing.
  - `source-notes/docs-promptfoo-assertions-metrics.md` — Claim 11
    (`skill-used` already listed in the telemetry-assertion family); this
    page adds the A/B protocol around the primitive rather than the
    primitive itself.
  - `source-notes/docs-promptfoo-configuration-guide.md` — Claim 12
    (array-var cartesian expansion and `disableVarExpansion` on
    `defaultTest.options`); relied on here (Claim 9), not re-derived.
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` — Claim 10
    (`--no-cache` / `--repeat 3` regression-gate discipline) and Claim 12
    (per-provider structured output: Codex `output_schema`, Claude
    `output_format.json_schema`, OpenCode `format`); this page applies both
    to the skill-swap design.
  - `source-notes/docs-promptfoo-max-score.md` — Claim 4 (`value.weights`
    keyed by assertion type); governs the weighting block in Claim 10 above.
  - `source-notes/docs-promptfoo-javascript-assertions.md` — Claim 1 (the
    `javascript` assertion's `{pass, score, reason}` contract); the recall
    scorer in Claim 7 is a consumer of that contract.
  - `source-notes/blog-anthropic-agent-skills.md` — Claim 2 (SKILL.md
    directory anatomy); this page is the *evaluation* layer on top of that
    packaging definition.
- **Contradicts**: none found. Checked `CONTRADICTIONS.md` (no open entry on
  skill evals or `skill-used`) and open `contradiction`-labeled issues; the
  closest surface is `docs-promptfoo-javascript-assertions.md` Claim 4's
  string-vs-object `output` conflict — this page's shared assertion handles
  both branches (`typeof output === 'string' ? JSON.parse(output) : output`)
  and attributes the divergence to the provider (Claim 6), which is
  complementary context, not an opposing claim. No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` — Claim 10
    (Python SDK lacks a first-class skill event; assert the observable
    workflow or return `metadata.skillCalls`): this page's per-provider
    evidence ladder (Claim 4) generalizes that gap into a strength ranking
    across Claude/OpenCode (first-class) vs Codex (inferred) vs Python
    (workflow proxy).
  - `source-notes/docs-promptfoo-evaluate-osworld-with-inspect.md` — its
    Extraction Notes name `test-agent-skills` as a sibling guide; no claim
    overlap (stateful VM grading vs skill routing), confirming distinct
    scope.
  - `source-notes/docs-langfuse-agent-skill.md` — Claims 3/10 (SKILL.md +
    `allowed-tools` frontmatter): this page shows how to regression-test that
    a skill's routing and behavior survive an edit to that frontmatter
    content.
- **Novel**: (1) the fixture-swap A/B methodology attributing behavioral
  deltas to `SKILL.md` text alone (Claim 1); (2) `skill-used` reframed as
  capability attribution / eval-validity precondition (Claim 2); (3) the
  three-layer bundle routing-boundary test with near-miss `not-skill-used`
  prompts (Claim 3); (4) the per-provider evidentiary-strength ladder for the
  same assertion name (Claim 4); (5) broad/narrow fixture pairing for
  scope-respect (Claim 8).

## Guide Impact

- **Chapter 03 (Runbooks and Agents — "Skills are the packaging unit for
  runbook knowledge", `guide/03-runbooks-and-agents.md:22`)**: The section
  currently defines what a skill *is* (citing `docs-langfuse-agent-skill`
  Claims 1/3) but gives no change-gate for editing one. Add: a SKILL.md edit
  is a behavior change and is evalable — one fixture dir per version, same
  model/tasks/permissions, swap only the skill file (this note Claim 1), with
  `skill-used` proving the route and a domain recall assertion proving the
  work (Claims 2, 7). Cite this note; do not restate the assertion mechanics
  owned by `docs-promptfoo-deterministic-metrics.md`.
- **Chapter 05 (LLM-ops reliability — "Grade the route, not just the reply",
  `guide/05-llm-ops-reliability.md:746`)**: That section lists `skill-used`
  among the trajectory assertions (citing `docs-promptfoo-deterministic-metrics`
  Claims 11-13). Extend it with the capability-attribution rule — a routing
  assert is what makes an outcome score attributable to the skill under test
  (Claim 2) — plus the bundle near-miss pattern (`not-skill-used` on the
  sibling, Claim 3) and the winner-selection discipline (`--repeat 3` /
  `--no-cache`, Claim 11), which reinforces the existing `--no-cache
  --repeat 5` fresh-sampling rule around `guide/05-llm-ops-reliability.md:579`.
- **Chapter 06 (Security and Trust — "Skills ship a tool allowlist at
  authoring time", `guide/06-security-and-trust.md:63`)**: That rule covers
  the static boundary (frontmatter allowlist). Add the dynamic counterpart:
  an allowlist is only exercised if routing sends the right traffic to the
  skill — regression-test routing boundaries with near-miss prompts asserting
  `skill-used` + `not-skill-used` (Claim 3), so a description edit that makes
  a skill over-trigger fails a gate instead of widening behavior in
  production. Evidence-strength caveat (Claim 4): on Codex the routing signal
  is an inferred file read, weaker proof than a Claude/OpenCode tool call.

## Extraction Notes

- Source read in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/test-agent-skills). **Sub-pages
  followed: none** — outbound links are sibling promptfoo guides
  (`evaluate-coding-agents`, `evaluate-osworld-with-inspect` — both already
  mined as their own notes), assertion/config reference pages (each with an
  existing note), the Claude/Codex SDK provider pages (config surface quoted
  inline on this page), and two GitHub example repos (the page reproduces the
  configs it needs); per MINER.md §1 nothing substantive was left to follow.
- Quotes verified character-for-character against the fetched rendered page
  before writing. Code blocks arrive as collapsed single lines after HTML
  extraction; line breaks were restored at YAML/bash/tree boundaries only,
  with no wording changes (same convention as the sibling promptfoo notes).
- **Candidate disposition** (from `miner-related-notes.md`, read before
  Cross-References; cited or dismissed by name):
  - `docs-promptfoo-evaluate-openai-agents-python.md` — **cited** (Extends,
    Claim 10, first-class-skill-event gap).
  - `docs-promptfoo-javascript-assertions.md` — **cited** (Corroborates,
    Claim 1, JS assertion return contract).
  - `docs-promptfoo-evaluate-coding-agents.md` — **cited** (Corroborates /
    Extends, Claims 10 and 12).
  - `docs-promptfoo-enterprise-findings-reports.md` — red-team finding
    disposition/export surface; no skill or eval-protocol content; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — skills as runbook packaging for an
    SRE triage agent; no evaluation methodology; dismissed.
  - `docs-google-sre-team-lifecycles.md`, `docs-google-sre-eliminating-toil.md`
    — SRE org/toil material; no LLM-eval content; dismissed.
  - `docs-promptfoo-llm-rubric.md`, `docs-promptfoo-pi-scorer.md` —
    model-graded judge semantics (audio grader, external scorer); not used by
    this page's deterministic-skill protocol; dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP transport; unrelated
    surface; dismissed.
  - Additional cross-refs beyond the candidate list were found by searching
    `source-notes/` per the Prospector's overlap list (deterministic-metrics,
    assertions-metrics, configuration-guide, max-score,
    blog-anthropic-agent-skills, evaluate-osworld-with-inspect,
    langfuse-agent-skill) — all verified per §4b before citing.
- Per the Prospector's scope guidance, deliberately NOT re-derived here:
  `skill-used`/`not-skill-used` assertion catalogue semantics,
  `max-score` weighting math, `cost`/`latency` assertion mechanics,
  `disableVarExpansion` matrix-expansion mechanics — owned by the notes cited
  in Cross-References; only this page's reliance on them is recorded.
- `confidence_overall` is `emerging`: mechanism/flag claims (Claims 4-7, 9,
  10, 12) are settled-for-product-behavior and checkable against installed
  CLIs, but the page reports no measured flake rates, pass rates, or
  before/after skill-quality data — the efficacy of the A/B protocol itself
  is vendor-asserted, first-party only.
- No contradiction issue filed (checked `CONTRADICTIONS.md` and open
  `contradiction`-labeled issues; see Cross-References).
- `registry/sources.json` and `registry/claims-index.json` were NOT edited —
  both are derived indexes rebuilt after merge.
