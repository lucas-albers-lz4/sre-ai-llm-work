---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-osworld-with-inspect
source_type: docs
title: "Promptfoo Guide: Evaluate OSWorld with Inspect — Stateful Desktop Grading, Error-vs-Failure Reconciliation, and the Harness-Observability Gap"
author: "Promptfoo (vendor documentation)"
date_published: 2026-10-15
date_extracted: 2026-10-15
last_checked: 2026-10-15
status: current
confidence_overall: emerging
issue: "#1724"
---

# Promptfoo Guide: Evaluate OSWorld with Inspect

> The vendor's guide to running a **stateful, VM-graded** computer-use benchmark
> (OSWorld) through an external harness (Inspect) with Promptfoo wrapping it as a
> `file://` provider — the page that makes denominator hygiene concrete: a
> three-state result model (pass / scored failure / provider error), a
> rerun-by-exact-`sample_id` policy that arbitrates which errors become scored
> outcomes, the "publish the raw run, the rerun policy, and the reconciled scored
> denominator together" rule, a two-layer timeout footgun, and an explicit
> observability gap where the desktop trajectory (mouse/keyboard/screenshot steps)
> stays inside Inspect and is invisible to Promptfoo's `trajectory:*` assertions.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo `/docs/guides/`
  guide page, discovered from the `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of a checked-in example
  (`integration-inspect-osworld`) that the vendor ships and runs; authoritative
  for what the wrapper does (provider shape, the three result states, the
  rerun procedure) and for the config mechanics. Vendor-positioned and
  single-run: the reference numbers are one local machine's run, the page says
  so explicitly ("This is not a stable leaderboard number"), and there is no
  independent replication. The page's own standard — "publish the raw run, the
  rerun policy, and the reconciled scored denominator together" — is the bar the
  note holds itself to.
- **Scope**: How to run OSWorld through Inspect under Promptfoo: what runs and
  the corpus sizes, the six-part wrapper, the three-state result model,
  prerequisites and Docker/VM sizing, the verification ladder (one sample → app
  slice → small suite → full corpus), the two execution-layer timeouts, result
  reading and `jq` denominator filters, the two reference GPT-5.5 runs with
  per-app breakdowns, Inspect log handling, the tracing bridge that does *not*
  exist yet, and a reimplementation checklist. It deliberately does **not**
  re-derive the generic `file://` provider `call_api` contract (sibling
  promptfoo notes own that) or the `trajectory:*` assertion catalogue; its
  payload is the stateful-benchmark operations discipline.
- **Last updated**: the page footer reads "Last updated on **Oct 15, 2026**";
  page undated, so `date_published` carries the last-updated date.

## Extracted Claims

### Claim 1: Stateful grading is the point — OSWorld grades the final VM/desktop state, not the agent's text, so an agent can answer `DONE` and still score `0.0`, which is the case for stateful graders over text assertions
- **Evidence**: The page's framing sentence in the intro and the paragraph
  after the task screenshot; the whole wrapper exists to route the OSWorld
  scorer result into a pass/fail.
- **Confidence**: settled (documented design of the benchmark and wrapper)
- **Quote**: "OSWorld is useful because success is not judged from the final text alone. An agent can answer `DONE` and still score `0.0` if the spreadsheet, slide deck, or desktop state is wrong. That makes it a concrete example of why agent evals need stateful graders, not only text assertions."
- **Our assessment**: This is the note's reason to exist and the sharpest
  counter-example the corpus has to text-only agent grading. It corroborates the
  coding-agents note's Claim 9 ("the agent's output *is* its final text
  response, not the files it changed") and gives the guide a benchmark-grade
  case where a `contains`/`llm-rubric` on the reply would score a wrong desktop
  as a pass. The rerun target (Claim 11) is the concrete demonstration: final
  answer `DONE`, scorer `0`. Buy it as a design claim; it is vendor-run but the
  mechanism (VM-state scorer) is checkable in the example.

### Claim 2: The wrapper splits responsibility cleanly — Promptfoo owns orchestration and reporting; Inspect owns the agent runtime and OSWorld grading
- **Evidence**: The "How the wrapper works" six-step list (provider called once
  per test case, starts `inspect eval`, Inspect runs sandbox/agent loop, writes
  `.eval`, provider runs `inspect log dump`, assertion reads the score) and the
  summarizing sentence.
- **Confidence**: settled (documented architecture, matches the shipped example)
- **Quote**: "This means Promptfoo owns orchestration and reporting. Inspect owns the agent runtime and OSWorld grading."
- **Our assessment**: This is the adapter-boundary claim the Prospector flagged
  as the separable piece. The value for the guide is that it names *where the
  failure can occur*: errors originating inside Inspect's runtime (Docker,
  computer tool) are not Promptfoo errors, which is exactly why they must be
  tracked separately (Claims 3-5). It also scopes the CI-gating question — the
  thing Promptfoo could gate on is the scorer output, not the trajectory.

### Claim 3: The provider treats results as a three-state model — `score >= 1.0` correct, `score < 1.0` scored failure, and provider `error` — with the error bucket covering setup, Docker, model SDK, timeout, tool execution, log parsing, or missing scorer output
- **Evidence**: The three bulleted states under "Implementation map" and the
  REST-style `status`/`score` example result object (Claim 12).
- **Confidence**: settled (documented product behavior, verifiable in the
  example's `provider.py`)
- **Quote**: "provider `error`: setup, Docker, model SDK, timeout, tool execution, log parsing, or missing scorer output prevented a scored sample from being produced."
- **Our assessment**: The taxonomy is the load-bearing claim for denominator
  discipline. Note the third state is *not* a score — it is the absence of one,
  which is why collapsing it into `0.0` corrupts the rate. The enumerated causes
  are the operational attack surface to watch (Docker, computer tool, scorer
  artifact). Buy it; it is the clearest statement in the corpus about what
  "unknown" means in an eval result.

### Claim 4: A failed score is a valid result, but a provider error is not — collapsing provider errors into failures corrupts the score, so the scorer output is only trustworthy when Inspect completed
- **Evidence**: The "Read the results" paragraph distinguishing `0.0` from
  errors, and the pass-rate computation section that filters `status != "error"`
  before dividing.
- **Confidence**: settled (documented rule)
- **Quote**: "A failed score is still a valid eval result when Inspect completed and the OSWorld scorer returned `0.0`. Treat provider errors differently: those indicate setup, Docker, model SDK, timeout, Inspect tool execution, or log parsing failures before a scored sample was produced."
- **Our assessment**: This is the denominator-hygiene statement the Prospector
  asked for. It pairs with the guide's existing "a green eval is not evidence
  until you can name what it measured" section — here the failure mode is the
  opposite polarity: an *unscored* row is not a failure and must not be counted
  as one. Buy it; it is directly reusable as a general rule for any eval whose
  harness can fail independently of the model.

### Claim 5: Rerun policy arbitrates the error→outcome boundary — rerun provider-error samples by exact `sample_id` at `--max-concurrency 1` before publishing a pass rate, and if the rerun scores, count it normally; if it errors again, report it separately
- **Evidence**: The "Read the results" rerun instruction and the full-corpus
  run where seven errors were rerun sequentially (Claim 11 lists the outcomes).
- **Confidence**: settled (documented procedure, executed in the reference run)
- **Quote**: "For benchmark reporting, rerun provider-error samples by exact `sample_id` with `--max-concurrency 1` before publishing a pass rate. If the rerun produces a score, count it as a normal pass or fail. If it errors again, inspect the `.eval` log and report it separately from scored OSWorld failures."
- **Our assessment**: The rule is the concrete answer to "what do you do with an
  errored row?" — you re-run it *isolated* (concurrency 1, exact id) so a flaky
  infrastructure error is separated from a deterministic one. This is a real
  operational procedure, not a framing claim, and it generalizes to any
  eval whose harness can fail. Buy it; the reference run gives it teeth.

### Claim 6: The publication rule — report the raw run, the rerun policy, and the reconciled scored denominator together, because provider errors are diagnostic evidence rather than failed attempts
- **Evidence**: The sentence closing the full-corpus section, immediately after
  the four repeated-error breakdown.
- **Confidence**: emerging (stated rule with one worked example; no independent
  replication)
- **Quote**: "This is why the guide treats provider errors separately from scored OSWorld failures. Publish the raw run, the rerun policy, and the reconciled scored denominator together."
- **Our assessment**: This is the reporting contract the note itself should be
  held to, and it directly extends the guide's evidence-quality theme: a pass
  rate is not reproducible unless the reader can see the denominator and the
  policy that produced it. It also gives the "repeated errors are useful
  diagnostic evidence" reframe (Claim 11). Buy the rule; note it is a single
  vendor example, hence `emerging`.

### Claim 7: There are two execution-layer timeouts and they are a misconfiguration trap — a Promptfoo Python-worker timeout in milliseconds and an Inspect subprocess timeout in seconds, defaulting to `1800000`/`1800` and raised to `7500000`/`7200` for the full suite
- **Evidence**: The "Configuration" section's two-timeout config block and the
  full-suite config block, plus the explanation that full-suite Writer rows can
  exceed the small config's 30-minute limit.
- **Confidence**: settled (documented config)
- **Quote**: "The provider config sets two timeouts because there are two execution layers:" and "It also raises the timeout budget because some full-suite Writer rows can exceed the small config's 30-minute limit:"
- **Our assessment**: A concrete silent-timeout footgun: the two knobs use
  different units (ms vs s) and both must be raised together, or the shorter one
  kills the run before the harness scores it — which would surface as a provider
  `error` (Claim 3), i.e. the exact denominator-corruption case. Buy it; it is
  the kind of specific, checkable trap the corpus values.

### Claim 8: There is an explicit observability gap — Promptfoo receives one provider span per sample plus result metadata, but the desktop trajectory lives in Inspect, so `trajectory:tool-used` cannot see the OSWorld mouse, keyboard, or screenshot steps without a bridge
- **Evidence**: The "Tracing" section stating what Promptfoo receives versus what
  stays in Inspect, and the sentence naming the assertions that cannot see the
  desktop steps.
- **Confidence**: settled (documented limitation of the shipped wrapper)
- **Quote**: "Promptfoo receives one provider span per sample plus result metadata: output text, score, token usage, sample id, status, and `inspect_log_path`." and "Without that bridge, Promptfoo trace assertions such as `trajectory:tool-used` cannot see the OSWorld mouse, keyboard, or screenshot steps."
- **Our assessment**: The genuine tracing-gap claim. It matters because the
  guide elsewhere treats `trajectory:*` as the way to assert the *path* an agent
  took — and this page shows a whole class of agents (computer-use / desktop)
  where the path is invisible to those assertions. The practical consequence:
  for stateful desktop agents, trace-level assertions are not the grading
  surface; the OSWorld scorer is. Buy it; it is a documented limitation, and it
  is the negative space of the coding-agents/bridge claims.

### Claim 9: Real cost/time/token figures for a stateful agent benchmark — a 21-sample small suite at concurrency 6 took 20m 9s and ~3.8M tokens; the 246-row full corpus took 5h 27m 5s and ~54.4M tokens (plus ~1.9M tokens for targeted reruns)
- **Evidence**: The two reference-run metric tables and the surrounding prose.
  Full corpus: main-run wall time `5h27m5s`, main-run token counter
  `54,421,072`, targeted rerun token counter `1,917,890`; small suite: wall time
  `20m 9s`, total token counter after rerun `3,806,976`.
- **Confidence**: emerging (single-run vendor numbers on one local machine; the
  page says "This is not a stable leaderboard number")
- **Quote**: "Avoid treating this as a cheap smoke test. OSWorld samples are slow, stateful, and token-heavy."
- **Our assessment**: This is the hard counter-evidence to "evals in CI" for
  stateful suites: 5h27m / 54.4M tokens for one full run on one machine. Record
  it as illustrative scale guidance, not a benchmark (the page says the full run
  is an Inspect-supported subset — 246 of 369 upstream tasks). The `emerging`
  grade reflects single-run, vendor-reported provenance.

### Claim 10: Concurrency is sized from the Docker VM's limits, not the host's — on a 6-vCPU/16-GiB Colima VM, `--max-concurrency 3` kept three desktop containers active without oversubscribing; a ~8GB image builds on first run and Docker Engine 24.0.6+/Compose V2 are required
- **Evidence**: The "Prerequisites" bullets, the first-run image-size sentence,
  and the full-corpus sizing paragraph.
- **Confidence**: settled (documented prerequisites and a stated sizing rule)
- **Quote**: "On a 6-vCPU, 16-GiB Colima VM, `--max-concurrency 3` kept three desktop containers active without oversubscribing the machine during the reference run. Choose concurrency from the Docker VM's limits, not only from the host machine's headline CPU and memory."
- **Our assessment**: The sizing rule is the operationally useful part — the
  desktop sandboxes consume the Docker VM's budget, and the host can have far
  more capacity than is actually usable (the page spells this out: "Use the
  Docker VM's CPU and memory limits as the sizing input"). This is a resource
  trap for anyone who sizes by `nproc` on the host. Buy it.

### Claim 11: Reruns separate flaky harness errors from deterministic ones — of seven full-corpus errors, three became scored outcomes (one pass, two failures) and four reproduced; the repeated four were computer-tool runtime, missing-image-artifact, and desktop-environment errors
- **Evidence**: The full-corpus run narrative ("After rerunning those seven rows
  sequentially... three became normal scored outcomes: one pass and two
  failures. Four reproduced as provider errors"), the four-error breakdown
  bullets, and the small-suite rerun target detail.
- **Confidence**: emerging (one run's sample; but a concrete, reproducible
  categorization)
- **Quote**: "After rerunning those seven rows sequentially with `--max-concurrency 1`, three became normal scored outcomes: one pass and two failures. Four reproduced as provider errors"
- **Our assessment**: This is the payoff of the rerun policy (Claim 5): it
  classifies each error as flaky (becomes a score) or deterministic (recurs),
  which is what lets the page call four errors "diagnostic evidence" rather than
  missing data. The small-suite target (Claim 11, Concrete Artifacts) is the
  clean single example: a concurrent `computer`-tool error, rerun alone,
  returned `DONE` and scored `0.0` because the PowerPoint comparison failed —
  proving the error had masked a genuine model failure. Buy the method; the
  specific counts are single-run.

### Claim 12: The assertion grades the OSWorld score, not the provider's final text — `assertion.py` passes only when the sample score is `1.0`, and missing per-sample scorer output is a provider error rather than a fallback to aggregate metrics
- **Evidence**: The wrapper step 6, the reimplementation checklist items 6-8
  ("require `samples[0].scores.osworld_scorer.value`... Treat missing per-sample
  scorer output as a provider error instead of falling back to aggregate
  metrics"), and the result-object example.
- **Confidence**: settled (documented design and explicit checklist rule)
- **Quote**: "Treat missing per-sample scorer output as a provider error instead of falling back to aggregate metrics."
- **Our assessment**: The discipline here is subtle and worth citing: when the
  per-sample score is absent, the correct action is to *fail closed into the
  error bucket*, not to reach for a suite-level aggregate that might silently
  include a different sample count. That is the same failure family as the
  guide's "a gate that cannot fail is not a gate" table. Buy it.

### Claim 13: Inspect `.eval` logs can contain sensitive screenshots and model outputs, so they must be kept out of git and not shared publicly
- **Evidence**: The "Inspect logs" section warning and the reimplementation
  checklist item 9.
- **Confidence**: settled (documented hygiene warning)
- **Quote**: "The `.eval` files can contain sensitive screenshots and model outputs, so keep them out of git and avoid sharing them publicly."
- **Our assessment**: A direct security/hygiene claim for stateful desktop
  evals: the artifact that makes desktop evals debuggable (screenshots) is also
  the one that leaks. It belongs with the guide's artifact-handling rules. Buy
  it; it is a plain, checkable instruction.

### Claim 14: The verification ladder is one exact `sample_id` → an app slice → the small suite → the full corpus, and the page explicitly warns against treating the benchmark as a cheap smoke test because samples are slow, stateful, and token-heavy
- **Evidence**: The "Run the example" progression, the five-scope list ("mockllm
  `--limit 0`", exact `sample_id`, app filter, full small suite, full config),
  and the closing "When to use this pattern" warning.
- **Confidence**: settled (documented procedure and explicit warning)
- **Quote**: "Start with one app or one exact `sample_id`, inspect the `.eval` log, then expand the sample set once the model and environment are stable."
- **Our assessment**: This is the gating guidance the Prospector asked for —
  not an endorsement of putting a 5-hour stateful suite on every PR, but a
  cost-ordered ladder that spends the least to validate the wrapper before
  spending the most. The explicit "avoid treating this as a cheap smoke test" is
  the counter-argument the note must carry alongside any CI-gating claim. Buy
  it.

### Claim 15: Aggregate pass rate hides structure — the per-app breakdown shows spreadsheets/documents as the strongest clusters and `multi_apps`/`vlc` as the weakest (and `vlc` also carried repeated harness-side errors)
- **Evidence**: The two per-app tables and the sentence interpreting them.
- **Confidence**: emerging (single-run breakdown)
- **Quote**: "Spreadsheet and document tasks were among the strongest clusters, while cross-app workflows and VLC were harder."
- **Our assessment**: The reporting lesson: "A single aggregate pass rate would
  hide both patterns" — capability spread across app classes *and* a
  harness-error cluster that happens to sit in the weakest group. Reporting the
  breakdown is what keeps a harness problem from reading as a model-quality
  problem. Buy the principle; the specific per-app numbers are one run.

## Concrete Artifacts

### The two-layer timeout config (verbatim from "Configuration" and the full-suite section)

```yaml
providers:
  - id: file://provider.py
    label: OSWorld via Inspect
    config:
      defaultModel: openai/gpt-5.5
      timeout: 1800000 # Promptfoo Python worker timeout, in ms
      timeoutSeconds: 1800 # Inspect subprocess timeout, in seconds
```

```yaml
providers:
  - id: file://provider.py
    config:
      timeout: 7500000 # Promptfoo Python worker timeout, in ms
      timeoutSeconds: 7200 # Inspect subprocess timeout, in seconds
```

### The wrapper invocation (verbatim from "How the wrapper works")

```
inspect eval inspect_evals/osworld_small \
  --model openai/gpt-5.5 \
  --sample-id 42e0a640-4f19-4b28-973d-729602b5a4a7 \
  --log-dir /absolute/path/to/inspect_logs/<run>
inspect log dump /absolute/path/to/inspect_logs/<run>/<file>.eval
```

### The three-state result model (verbatim from "Implementation map")

- `score >= 1.0`: Inspect completed and OSWorld scored the task as correct.
- `score < 1.0`: Inspect completed and OSWorld scored the task as incorrect.
- provider `error`: setup, Docker, model SDK, timeout, tool execution, log parsing, or missing scorer output prevented a scored sample from being produced.

### The provider's returned result object (verbatim from "Read the results")

```json
{
  "inspect_log_path": "/absolute/path/to/inspect_logs/.../*.eval",
  "score": 0.0,
  "status": "fail",
  "sample_id": "42e0a640-4f19-4b28-973d-729602b5a4a7",
  "model": "openai/gpt-5.5",
  "num_messages": 58,
  "duration_seconds": 617.32,
  "task": "inspect_evals/osworld_small",
  "app": "libreoffice_calc"
}
```

### Reference small-suite run — 21 samples, GPT-5.5 (verbatim table)

| Metric | Result |
|---|---|
| Eval id | `eval-7hQ-2026-04-28T02:52:18` |
| Error rerun eval id | `eval-3rI-2026-04-28T03:30:43` |
| Samples | 21 |
| Concurrency | 6 |
| Wall time | 20m 9s |
| Passed | 13 / 21 |
| Scored failures after rerun | 8 / 21 |
| Provider errors after rerun | 0 / 21 |
| Mean OSWorld score | 0.665 |
| Promptfoo trace records | 21 |
| Promptfoo Python provider spans | 21 |
| Total token counter after rerun | 3,806,976 |

### Reference full-corpus run — 246 samples, GPT-5.5 (verbatim table)

| Metric | Result |
|---|---|
| Samples | 246 |
| Scored rows after reruns | 242 |
| Passed | 139 |
| Scored failures after reruns | 103 |
| Provider errors after reruns | 4 |
| Pass rate over scored rows | 57.4% |
| Mean OSWorld score | 0.594 |
| Main-run wall time | 5h27m5s |
| Main-run token counter | 54,421,072 |
| Targeted rerun token counter | 1,917,890 |

Raw full-corpus run before reruns: "138 passes, 101 scored failures, and 7
provider errors."

### The repeated provider errors (verbatim bullets from the full-corpus section)

- one `libreoffice_impress` row repeated an Inspect computer-tool runtime error
- one `multi_apps` row repeated an OSWorld scorer missing-image-artifact error
- two `vlc` rows repeated an OSWorld scorer desktop-environment error

### Rerun target detail (verbatim from the small-suite run)

> "The rerun target was `multi_apps` sample `eb303e01-261e-4972-8c07-c9b4e7a4922a`, a task that asks the agent to insert speaker notes into a PowerPoint file. The original concurrent attempt errored inside Inspect's `computer` tool while executing a model-requested desktop command. The isolated rerun completed in 7m 44s, used 288,447 total tokens, returned final answer `DONE`, and failed only because the OSWorld scorer reported `compare_pptx_files(...) returned 0`."

### Denominator-filter `jq` (verbatim from "Read the results")

```bash
jq '[.results.results[] | select((.response.metadata.status // "") != "error")] | length' \
  osworld-full-results.json
jq -r '.results.results[]
  | select((.response.metadata.status // "") == "error")
  | [.vars.app, .vars.sample_id, .response.error]
  | @tsv' osworld-full-results.json
```

### Tracing config (verbatim from "Configuration")

```yaml
tracing:
  enabled: true
  otlp:
    http:
      enabled: true
      port: 4318
      host: 127.0.0.1
      acceptFormats:
        - json
        - protobuf
```

Run commands are wrapped with `PROMPTFOO_ENABLE_OTEL=true` and
`OTEL_EXPORTER_OTLP_ENDPOINT=http://127.0.0.1:4318`, and the Python provider
"records a child span with the prompt, response, token usage, status, eval id,
and test case id."

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 9** ("An
    agent's output *is* its final text response, not the files it changed — so
    file-level verification must inspect the workspace or enable tracing") —
    this page is the stateful, VM-graded instance of that claim: the agent's
    `DONE` is a self-report and the OSWorld scorer grades the desktop instead
    (Claim 1). (Verified: #1680 Claim 9, read in full.)
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 10**
    (regression gates are cost/latency thresholds plus `--no-cache` and
    `--repeat 3`, with a concrete cost band) — corroborates this page's "not a
    cheap smoke test" cost framing and its token/time accounting (Claims 9, 14):
    both notes treat the eval's dollar/wall-clock footprint as a first-class
    gate input rather than an afterthought. (Verified: #1680 Claim 10.)
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` **Claim 4**
    (two OTLP encodings accepted; the opt-in `PROMPTFOO_ENABLE_OTEL=true` adds a
    provider-level parent span) and **Claim 2** (the W3C-`traceparent` →
    provider-span bridge) — this page reuses exactly that bridge shape (one
    provider span per sample under a `traceparent`) for a shell-out provider
    rather than an SDK provider (Claim 8). (Verified: #1707 Claims 2, 4.)
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` **Claim 8**
    (Promptfoo does **not** infer a dollar `cost` on the agent path; return
    `cost` only when every billed model and hosted tool can be accounted for) —
    corroborates why this page reports *tokens* (e.g. `3,806,976`,
    `54,421,072`) rather than a dollar figure for the OSWorld runs.
    (Verified: #1707 Claim 8.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 12** (the
    trace/trajectory assertion family requires trace data and throws when traces
    are unavailable) — the config-level statement behind this page's
    observability gap: `trajectory:tool-used` needs trace data, and for OSWorld
    that data is inside Inspect, not Promptfoo (Claim 8). (Verified: #1289 Claim
    12.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 6** (the
    `cost` assertion can only gate provider-reported cost; fresh-cost gating
    requires `--no-cache`) — the sibling rule to this page's token-counter
    reporting and its `--no-cache` run commands (Claims 9, 14). (Verified:
    #1289 Claim 6.)

- **Contradicts**: None identified, and no contradiction issue filed. This is
  first-party vendor documentation of one guide page and opposes no existing
  source-note claim. Checked `CONTRADICTIONS.md` and open `contradiction`-labeled
  issues — nothing on OSWorld/Inspect, stateful desktop grading, eval-harness
  error accounting, or multi-layer timeouts. The nearest neighbours (the
  coding-agents and openai-agents-python notes) are complementary: they own the
  agent-eval methodology and the provider-adapter contract, and this page adds a
  stateful/VM-graded benchmark and the error-vs-failure reconciliation they do
  not cover. No conflict, so no contradiction issue was filed.

- **Extends**:
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 1**
    (an agent eval tests a *system with emergent behavior*) and **Claim 2**
    (capability tiers) — this page is a new tier in that framing: instead of a
    coding-agent SDK, the runtime is a full desktop sandbox reached by shelling
    out to a third-party harness (Inspect), and the grade is VM state rather
    than an assertion on the response. (Verified: #1680 Claims 1, 2.)
  - `source-notes/docs-promptfoo-evaluate-crewai.md` **Claim 1** (a locally
    defined agent is evaluated by pointing a `file://` provider at a Python
    file) and `source-notes/docs-promptfoo-evaluate-google-adk.md` **Claim 1**
    (wrap the app as an in-process Python provider) — the same `file://` provider
    shape, extended here to a provider whose `call_api` shells out to an
    external process (`inspect eval` / `inspect log dump`) and parses a
    per-sample score from a dumped log instead of returning agent output
    directly (Claim 2, Claim 12). (Verified: #1681 Claim 1, #1694 Claim 1.)
  - `source-notes/docs-promptfoo-evaluate-openai-agents-python.md` **Claim 8**
    and `docs-promptfoo-deterministic-metrics.md` **Claim 12** — carried forward
    as the cost-accounting and trace-dependency boundaries this page works
    within, not re-derived.

- **Novel**:
  - The first source in the corpus to grade an agent on **stateful VM/desktop
    state** rather than text or a workspace diff, and to state the
    `DONE`-but-score-`0.0` failure mode explicitly (Claim 1).
  - The first **three-state eval result model** with an enumerated provider-error
    taxonomy and the rule that errors are not failures (Claims 3-4).
  - The first documented **rerun-by-exact-`sample_id` at concurrency 1** policy
    as the arbiter of the error→outcome boundary, with flaky-vs-deterministic
    error classification (Claims 5, 11).
  - The first **two-execution-layer timeout** footgun (ms vs s; worker vs
    subprocess) in the corpus (Claim 7).
  - The first explicit **desktop-trajectory observability gap** — a whole class
    of agents whose actions are invisible to `trajectory:*` assertions without a
    custom bridge (Claim 8).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability) — "A green eval is not evidence until you
  can name what it measured" (`guide/05-llm-ops-reliability.md:567`)**: Add a
  companion rule for the *denominator*, not just the numerator: an eval whose
  harness can fail independently of the model must report three states (scored
  pass / scored failure / provider error) and must publish the raw run, the
  rerun policy, and the reconciled scored denominator together — because
  collapsing provider errors into failures corrupts the rate (Claims 3, 4, 6).
  The concrete policy: rerun errored rows by exact `sample_id` at concurrency 1
  and count a rerun that scores normally, report a recurring error separately
  (Claims 5, 11) [source: docs-promptfoo-evaluate-osworld-with-inspect, Claims
  3, 4, 5, 6, 11] [emerging]. This is the denominator-side analogue of the
  chapter's existing cache/staleness warnings.
- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: Add stateful/VM-graded benchmarks
  as the case where the *grading surface is the harness's scorer, not the
  model's text* — `assertion.py` passes only on `score == 1.0`, and missing
  per-sample scorer output must fail closed into the error bucket rather than
  fall back to an aggregate (Claim 12). Also record the cost counter-evidence:
  the full corpus is 246 rows / 5h27m / 54.4M tokens, so a stateful suite is a
  nightly or on-demand gate, not a per-PR gate, and its concurrency is sized
  from the Docker VM, not the host (Claims 9, 10, 14) [source:
  docs-promptfoo-evaluate-osworld-with-inspect, Claims 9, 10, 12, 14]
  [emerging].
- **Chapter 02 (Observability) — instrumenting tool calls
  (`guide/02-observability.md:50`)**: Record the tracing gap as a boundary of
  the "instrument every tool call" rule: when an agent's runtime lives in an
  external harness (Inspect) that emits its own log format, Promptfoo sees one
  provider span per sample plus metadata, and the desktop mouse/keyboard/
  screenshot steps stay outside the trace — so `trajectory:tool-used` cannot
  observe them without a custom Inspect→OTel bridge (Claim 8), and the trace
  assertions that the chapter relies on throw when that data is absent
  [source: docs-promptfoo-evaluate-osworld-with-inspect, Claim 8; and
  docs-promptfoo-deterministic-metrics, Claim 12] [settled].
- **Chapter 03 (Runbooks and Agents) — sandboxing and trajectory evaluation
  (`guide/03-runbooks-and-agents.md:136`)**: Add the stateful-grading rationale
  for trajectory-level evaluation — OSWorld grades the final VM state, so an
  agent can answer `DONE` and still score `0.0`; text assertions are insufficient
  for computer-use agents (Claim 1). Pair it with the two-layer timeout trap
  (`timeout` in ms vs `timeoutSeconds` in s; raise both together or the run
  becomes a provider error) as an operational note for anyone running a desktop
  agent through an eval wrapper (Claim 7) [source:
  docs-promptfoo-evaluate-osworld-with-inspect, Claims 1, 7] [emerging].
- **Chapter 06 (Security and Trust) — artifact handling**: Add the desktop-eval
  hygiene rule: Inspect `.eval` logs contain screenshots and model outputs and
  must be kept out of git and not shared publicly — the debug artifact that makes
  desktop evals reviewable is also the leak surface (Claim 13) [source:
  docs-promptfoo-evaluate-osworld-with-inspect, Claim 13] [settled].

## Extraction Notes

- Source read in full via direct fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/evaluate-osworld-with-inspect). It is a
  single self-contained guide page. **Sub-pages followed: none** — the outbound
  links are `inspect.aisi.org.uk`, the `integration-inspect-osworld` example
  directory, the linked OSWorld arXiv paper, and sibling promptfoo guide pages
  (`evaluate-coding-agents`, `test-agent-skills`) that are already mined or are
  separate sources. The page reproduces every config and result it needs inline;
  per MINER.md §1 non-sibling follows were unnecessary and the example repo was
  not cloned (its contents are quoted in the page).
- **Scope discipline (per the Prospector's "mine the delta")**: deliberately not
  re-derived here are the generic `file://` provider `call_api` contract (owned
  by `docs-promptfoo-evaluate-crewai.md` / `docs-promptfoo-evaluate-google-adk.md`)
  and the `trajectory:*` assertion catalogue (owned by
  `docs-promptfoo-deterministic-metrics.md`). This note extracts the *stateful
  benchmark operations discipline* — three-state results, rerun policy,
  denominator reconciliation, timeouts, sizing, the observability gap — and
  cites the primitives by claim.
- Quotes were verified character-for-character against the fetched rendered
  page. Code blocks arrive as collapsed single lines after HTML extraction;
  line breaks were restored at YAML/JSON/bash boundaries only (no wording
  changes), and the two reference-run tables were copied row-for-row. The
  three-state bullets and the repeated-error bullets are quoted as the page's
  own list items.
- **Cross-ref verification (§4b)**: every cited claim number was located in the
  cited note and its content checked against what it is cited for — #1680 Claims
  1/2/9/10, #1681 Claim 1, #1694 Claim 1, #1289 Claims 6/12, and #1707 Claims
  2/4/8.
- **Candidate list (`miner-related-notes.md`) disposition**: cited —
  `docs-promptfoo-evaluate-coding-agents.md` (Corroborates Claims 9-10; Extends
  Claims 1-2) and `docs-promptfoo-evaluate-openai-agents-python.md`
  (Corroborates Claims 2, 4, 8). Explicitly dismissed as lexically related but
  substantively off-target (no overlapping claim cited):
  `docs-promptfoo-enterprise-findings-reports.md` (red-team finding disposition,
  different surface), `docs-litellm-batches-api.md` (gateway batch rate limiting,
  not eval-harness errors), `blog-pagerduty-sre-agent-triage.md` (incident
  triage, not benchmarking), `docs-langfuse-mcp-server.md` (docs MCP access),
  `docs-google-sre-team-lifecycles.md` (SRE org design),
  `blog-promptfoo-owasp-red-teaming.md` (red-team phases),
  `docs-promptfoo-enterprise-audit-logging.md` (control-plane audit events),
  `docs-promptfoo-enterprise-guardrails.md` (runtime guardrail enforcement).
  Two additional cross-refs were discovered by searching `source-notes/`
  (`docs-promptfoo-evaluate-crewai.md`, `docs-promptfoo-evaluate-google-adk.md`).
- **Vendor caveat carried forward**: the reference-run numbers are single-run,
  vendor-reported, on one local machine, and the page itself says they are "not a
  stable leaderboard number" and that the full run is an Inspect-supported subset
  of the upstream OSWorld corpus (246 of 369). The reconciled post-rerun figures
  (139 pass / 103 scored failure / 4 provider errors over 242 scored rows, 57.4%,
  mean 0.594) are recorded in preference to the raw pre-rerun counts
  (138 / 101 / 7), per the Prospector's caveat. The small suite reports no
  overall percentage, only 13/21 passed with 8/21 scored failures after rerun.
  The note does not claim an independent benchmark result or a demonstrated
  CI-gating pattern; CI gating for stateful suites is mentioned by the page only
  as a possible use ("Add Promptfoo assertions or CI gates around Inspect's
  scorer output") and is *not* demonstrated.
