---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-google-adk
source_type: docs
title: "Promptfoo: Evaluate Google ADK Agents — In-Process Provider vs HTTP App Server, the Feature→Assertion Mapping, and the Framework-Version Coupling Hazard"
author: "Promptfoo (vendor documentation; page by Michael D'Angelo)"
date_published: 2026-10-13
date_extracted: 2026-10-13
last_checked: 2026-10-13
status: current
confidence_overall: emerging
issue: "#1694"
---

# Promptfoo: Evaluate Google ADK Agents

> A vendor recipe for driving a Google ADK app under promptfoo by wrapping the
> **ADK runtime in process** behind a Python provider, so one eval row can read
> session state, drain artifacts, observe plugin/callback events, and assert
> over ADK's native OTel trajectory spans — the page's reusable payload is the
> **eval-surface decision** (in-process provider vs `adk api_server` HTTP), a
> **framework-feature → assertion mapping** method, and the **version-coupling
> hazard** (an eval pinned to a framework's internal event schema breaks across
> a major version bump). It carries **no** CI gating, thresholds, or baselines.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Evaluate Google ADK
  Agents", under Evals → Guides → Integrations; auto-discovered from the
  registered `promptfoo-docs` site-crawl seed). Single guide page, no sub-pages
  followed.
- **Author credibility**: Promptfoo, the LLM eval / red-team vendor. First-party
  documentation of the product's own Python-provider and ADK binding — the
  documented config, code, and span shapes are authoritative and directly
  checkable against an installed CLI, but vendor-positioned: no run results, no
  metrics, no independent validation, and the ADK binding is demonstrated only
  against the vendor's own scaffolded example. The page footer credits Michael
  D'Angelo.
- **Scope**: Covers (1) an `npx promptfoo@latest init --example
  integration-google-adk` scaffold and prerequisites; (2) why an in-process
  Python provider beats the `adk api_server` HTTP shape; (3) how ADK's native
  OTel spans flow into promptfoo's OTLP receiver (`invocation`,
  `invoke_agent <name>`, `call_llm`, `execute_tool <tool>`); (4) extracting
  sessions/state/plugins/artifacts as one JSON payload; (5) workflow agents
  (`SequentialAgent` → `Workflow`); (6) a framework-feature → assertion mapping
  table; (7) production notes; and (8) a harness-selection rule (`adk eval` vs
  promptfoo). Does NOT cover: CI gating, thresholds, baseline comparison,
  regression suites, or findings triage/export.
- **Last updated**: Oct 13, 2026 (page footer: "Last updated on **Oct 13, 2026**
  by **Michael D'Angelo**") — same day as extraction, so `date_published` carries
  the last-updated date.

## Extracted Claims

### Claim 1: The recommendation is to wrap an ADK app as an **in-process Python provider**, because that is what makes the agent's sessions, artifacts, plugin/callback side effects, and native trajectory spans assertable — the HTTP shape around `adk api_server` cannot expose any of those "without a parallel inspection channel"
- **Evidence**: The "Why Use A Python Provider" section's consequence sentence
  and the opening summary line ("That keeps the ADK runtime in process, so
  Promptfoo can inspect the same sessions, artifacts, and native OpenTelemetry
  spans that the agent produced."). The Prospector flagged this as the page's
  generalizable eval-surface trade-off.
- **Confidence**: settled (documented design rationale; every example on the page
  uses the Python provider)
- **Quote**: "An in-process Python provider lets one Promptfoo row drive a
  multi-turn task, read session state, load artifacts, observe plugin and
  callback side effects, and assert against ADK's native trajectory spans — all
  without going over the wire. The HTTP shape around `adk api_server` cannot
  expose any of those without a parallel inspection channel."
- **Our assessment**: This is the page's transferable core and the reason it is
  worth a separate note: it recasts "which provider do I use?" as a *test-scope
  decision*. The in-process provider is the mechanism by which an eval row can
  see **agent-internal state** rather than only the HTTP response body — which is
  exactly the gap `docs-promptfoo-evaluate-coding-agents.md` Claim 9 names ("The
  agent's output is its final text response describing what it did, not the file
  contents"). Buy the framing; the ADK-specific plumbing is scaffolding.

### Claim 2: HTTP is the *complementary* choice, preferred only when the deployed HTTP contract itself is what you want to validate
- **Evidence**: The closing two sentences of the same section, framed as an
  either/or rule.
- **Confidence**: settled (documented guidance)
- **Quote**: "Pick the HTTP provider when the deployed HTTP contract itself is
  what you want to validate (auth, request shape, status codes). Pick the Python
  provider for everything else."
- **Our assessment**: The one-line decision rule is the extractable bit: the two
  providers answer different questions (deployed-contract conformance vs
  agent-behavior inspection), so the choice is conditioning on *what is under
  test*, not a preference. Note the page does not claim the two surfaces are
  equivalent in coverage — in-process is a superset for behavior, HTTP is the
  only one that exercises the real wire contract.

### Claim 3 (carry-forward, not re-extracted): The concrete assertions the page reaches for are the corpus's existing trajectory/trace family — `trajectory:tool-used`, `trajectory:tool-args-match`, `trajectory:tool-sequence`, plus `trace-span-count` and `trace-error-spans`
- **Evidence**: The "How Native ADK Tracing Fits Promptfoo" YAML block, used to
  assert `get_weather` / `save_trip_note` tool use, partial argument matching on
  `city: London`, and tool order.
- **Confidence**: settled (documented config; primitives already catalogued)
- **Quote**: "Use `trace-span-count` and `trace-error-spans` alongside trajectory
  assertions when you also want to prove that the ADK runtime emitted the
  expected framework spans and stayed error-free."
- **Our assessment**: This is a **reuse**, not new material — the assertion
  primitives are owned by `docs-promptfoo-deterministic-metrics.md` (Claims 11–13)
  and `docs-promptfoo-assertions-metrics.md` (Claim 11), and the "assert the path
  when the path matters" methodology by `docs-promptfoo-evaluate-coding-agents.md`
  (Claim 7). Extract the ADK binding only; do not re-derive the primitives.

### Claim 4: ADK already emits OTel GenAI spans with `gen_ai.tool.name` and tool-call arguments, so promptfoo can normalize them into trajectory steps **without a custom span translator**
- **Evidence**: The span list (`invocation`, `invoke_agent weather_agent`,
  `call_llm`, `execute_tool get_weather`) and the sentence crediting ADK's native
  attributes.
- **Confidence**: settled for the vendor-stated span shapes (documented on the
  page; the Prospector notes these are vendor-stated, not reproduced)
- **Quote**: "ADK already records `gen_ai.tool.name` and tool-call arguments, so
  Promptfoo can normalize them into trajectory steps without a custom span
  translator."
- **Our assessment**: The `invoke_agent <name>` / `execute_tool <tool>` shapes are
  the **same** OTel GenAI span-naming contract documented from the
  instrumentation side at
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claims 6 and 12 — here
  asserted *from the eval side*. The "no custom span translator" point is the
  interoperability payoff: when the framework emits conformant spans, the eval
  harness consumes them for free.

### Claim 5: The provider preserves promptfoo's W3C `traceparent`, starts a small provider span beneath it, and exports ADK's child spans to promptfoo's built-in OTLP receiver — so the eval and the observability trace are one trace
- **Evidence**: The "How Native ADK Tracing Fits Promptfoo" paragraph on
  `traceparent` preservation and the OTLP receiver, plus the Trace Timeline
  bullets ("one Promptfoo provider span beneath the injected parent trace").
- **Confidence**: settled (documented behavior)
- **Quote**: "The example provider preserves Promptfoo's W3C `traceparent`,
  starts a small provider span beneath it, and exports ADK's child spans to
  Promptfoo's built-in OTLP receiver."
- **Our assessment**: This is the mechanism behind the trace-coupling risk already
  recorded at `docs-promptfoo-deterministic-metrics.md` Claim 12 (trace/trajectory
  assertions throw when trace data is unavailable). Read together: the eval gate
  and the observability trace share a parent, which is powerful — and means the
  eval run's health depends on the OTLP export staying live.

### Claim 6: The provider returns one JSON payload of agent-internal effects — `artifact_names`, `plugin_events`, `session_state` — which deterministic `contains`/`is-json` assertions can check **without a model grader**
- **Evidence**: The "Sessions, State, Plugins, And Artifacts" section's JSON
  payload and the sentence "Deterministic `contains` and `is-json` assertions can
  then check internal effects without a model grader".
- **Confidence**: settled (documented code/config)
- **Quote**: "One eval row now covers the assistant's reply *and* the agent's
  internal bookkeeping."
- **Our assessment**: This is the concrete answer to "what does in-process buy
  you?" The eval becomes a *state* test, not just a text test: the artifact name,
  the callback-invocation count, and the last-saved-artifact key are all
  assertable. It is the agent-internal analogue of the workspace-inspection
  metadata at `docs-promptfoo-evaluate-coding-agents.md` Claim 6 (`workingDir`,
  `workspaceDiff`) — both let an assertion read what actually happened instead of
  what the model said happened.

### Claim 7: For every distinct ADK feature there is a mapped assertion type — a **method for deriving assertions** rather than a fixed catalogue
- **Evidence**: The "Structured Outputs, Memory, And Advanced Tools" table, whose
  left column is ADK features (`output_schema`/`output_key`, `MemoryService`,
  MCP/OpenAPI/auth tools, code executors, multi-agent trees, long-running apps)
  and right column is the assertion that proves the feature works.
- **Confidence**: settled (documented mapping; the Prospector called this "the
  genuinely novel artifact on this page")
- **Quote**: "The same provider shape covers the other ADK features. Map each ADK
  feature to the assertion type that proves it works:"
- **Our assessment**: This is the page's most reusable contribution for the
  guide: it reframes assertion selection as "what capability does this framework
  feature provide, and what is the deterministic proof it fired?" — e.g.
  `output_schema` → `is-json` + `contains`; `MemoryService` → paired cases with
  shared vs distinct session ids; multi-agent trees → one `trace-span-count` per
  `invoke_agent <name>`. The complete table is reproduced in Concrete Artifacts.
  It complements the coding-agent provider-tier baseline rule
  (`docs-promptfoo-evaluate-coding-agents.md` Claim 2): tier picks *what you can
  assert on*, this mapping picks *which assertion proves it*.

### Claim 8: Fixed-order work should be encoded as a workflow agent (not left to the LLM to route), and each named workflow agent earns its own `trace-span-count`
- **Evidence**: The "Workflow Agents" section's `SequentialAgent` example
  (`weather_lookup_agent` → `briefing_agent`) and the closing guidance.
- **Confidence**: settled (documented guidance + code)
- **Quote**: "When the order of work is fixed, encode it as a workflow agent
  instead of relying on the LLM to route." and "Add a `trace-span-count` for each
  named workflow agent, and keep `trajectory:tool-used` focused on the tool calls
  that must happen."
- **Our assessment**: The trace-span-per-agent rule is the **producer-side**
  requirement for the multi-agent swim-lane pattern documented from the
  instrumentation side at
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claim 6 ("Sub-agents
  use their own distinct names; they don't inherit from the parent."). Here the
  eval asserts one span per named agent, which only works if the runtime names
  each agent distinctly — the two notes bound the producer and consumer halves of
  the same contract.

### Claim 9: An eval harness pinned to a framework's **internal event schema** is a migration hazard — ADK 1.x → 2.x changes persisted event schemas (`node_info`, `output`), changes custom execution overrides, and shifts retry/emission ownership to the runtime, and 2.9.2 deprecates `SequentialAgent` in favor of `Workflow`
- **Evidence**: The page's top-of-page `note` callout (with its explicit
  recommendation to review ADK's migration guidance before upgrading a production
  app) and the "Workflow Agents" sentence on the 2.9.2 deprecation.
- **Confidence**: settled for the documented version changes; the *interpretation*
  that this endangers an eval harness is our synthesis (the Prospector called it
  "the concrete, transferable claim")
- **Quote**: "Before upgrading a production app, review ADK's migration guidance:
  persisted event schemas gain `node_info` and `output`, custom execution
  overrides change, and the runtime must own event emission and retries." and "ADK
  2.9.2 deprecates `SequentialAgent` in favor of `Workflow`, but still supports the
  sequential-agent example below."
- **Our assessment**: This is the version-coupling hazard the guide's release
  discipline (Ch05) cares about: because the eval asserts over framework-internal
  event schemas and span shapes, a framework major-version bump can break the eval
  *silently* — the assertions still run but match nothing the runtime now emits.
  The page states the migration facts but does not itself connect them to eval
  stability; that connection is our synthesis and should be labeled as such in
  the guide.

### Claim 10: Operational determinism guidance for an in-process provider — keep the provider span small, flush before the worker exits, use in-memory services for determinism, and swap in real services only when persistence is the behavior under test
- **Evidence**: The "Production Notes" bullets.
- **Confidence**: settled (documented vendor guidance)
- **Quote**: "Keep the provider span small. ADK emits the framework spans; the
  wrapper only has to preserve Promptfoo's parent trace and flush before the worker
  exits." and "The bundled example uses in-memory services so runs are
  deterministic. Swap in your real `SessionService`, `ArtifactService`, or
  `MemoryService` when persistence is part of the behavior under test."
- **Our assessment**: Two reusable rules. (a) The wrapper should not re-instrument
  — ADK already emits the framework spans, so the provider's only job is to
  preserve the parent trace and flush, or spans are lost on worker exit (the
  buffering trap). (b) In-memory-vs-real services is a determinism/fidelity
  trade-off identical in shape to the coding-agent note's `copy_working_dir`
  choice: use the fast deterministic stand-in unless the persistence *is* what you
  are testing.

### Claim 11: Reserve model-graded assertions for genuinely semantic outcomes; prefer state/artifact assertions first
- **Evidence**: The third production-note bullet naming tone, factuality, and
  refusal quality as the semantic cases.
- **Confidence**: settled (documented guidance)
- **Quote**: "Reach for state and artifact assertions first; reserve model-graded
  assertions for outcomes that actually require semantics (tone, factuality,
  refusal quality)."
- **Our assessment**: This is the same deterministic-first discipline the corpus
  already carries (`docs-promptfoo-assertions-metrics.md` Claim 10's
  deterministic/model-assisted split; `docs-promptfoo-evaluate-coding-agents.md`
  Claim 12's structured-output-first rule). It matters here because the in-process
  provider creates the *option* to assert on state — so the guidance is "use the
  new capability before reaching for a judge," not a new principle.

### Claim 12: The harness-selection rule — use the framework's own eval (`adk eval`) for framework-native eval sets and metrics; use promptfoo when comparing across frameworks, running red teams on the same surface, or asserting on OTel traces alongside the final output
- **Evidence**: The closing paragraph of "Structured Outputs, Memory, And
  Advanced Tools".
- **Confidence**: settled (documented vendor positioning)
- **Quote**: "ADK ships its own `adk eval` stack — use it for ADK-native eval sets
  and ADK-specific metrics. Promptfoo is the better fit when one harness has to
  compare ADK against other frameworks, run red teams against the same surface, or
  assert on OpenTelemetry traces alongside the final output."
- **Our assessment**: A vendor-drawn boundary worth recording because it is
  self-limiting: promptfoo's claimed moat is *cross-framework comparison* and
  *one red-team surface*, not "replace your framework's eval." It is the
  harness-level analogue of the coding-agent provider-tier baseline rule (run the
  plain-LLM baseline to prove the harness contributes).

### Claim 13 (explicit gap): The page contains **no** CI gating — eval runs are manual `npx promptfoo@latest eval` / `view` commands, with no pipeline file, threshold, baseline comparison, or commit-triggered run anywhere
- **Evidence**: Every execution step is an interactive CLI call (Quick Start and
  the workflow variant both run `eval ... --no-cache` by hand); no workflow/CI
  file, threshold, or baseline appears on the page.
- **Confidence**: settled (absence — verified by reading the full page; the
  Prospector flagged the same gap)
- **Quote**: "npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache"
- **Our assessment**: The anti-over-claim to preserve. Any guide framing of this
  page as an eval *gate* would be an extrapolation it does not support. It
  demonstrates harness *mechanics* (provider shape, state/artifact assertions,
  span normalization, feature→assertion mapping), not eval-in-CI *practice*. This
  is the same gap as the CrewAI sibling
  (`docs-promptfoo-evaluate-crewai.md` Claim 9).

## Concrete Artifacts

All artifacts copied from the source page
(https://www.promptfoo.dev/docs/guides/evaluate-google-adk), sections named.
Code blocks arrive as collapsed single lines after HTML extraction; line breaks
were restored at code/config boundaries only, with no wording changes.

### Quick Start (verbatim from "Quick Start")

```
npx promptfoo@latest init --example integration-google-adk
cd integration-google-adk
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export GOOGLE_API_KEY=your_google_api_key_here
npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache
npx promptfoo@latest eval -c promptfooconfig.workflow.yaml --no-cache
npx promptfoo@latest view
```

### ADK agent under test (verbatim from "What The Example Covers")

```python
root_agent = Agent(
    name="weather_agent",
    model=model,
    instruction="...travel weather assistant. Call get_weather... Call save_trip_note...",
    tools=[get_weather, save_trip_note],
    before_agent_callback=before_agent_callback,
)
app = App(name=APP_NAME, root_agent=root_agent, plugins=[audit_plugin])
```

### Native ADK span shapes to assert on (verbatim from "How Native ADK Tracing Fits Promptfoo")

```
invocation
invoke_agent weather_agent
call_llm
execute_tool get_weather
```

### Trajectory assertions (verbatim YAML from "How Native ADK Tracing Fits Promptfoo")

```yaml
assert:
  - type: trajectory:tool-used
    value:
      - get_weather
      - save_trip_note
  - type: trajectory:tool-args-match
    value:
      name: get_weather
      args:
        city: London
      mode: partial
  - type: trajectory:tool-sequence
    value:
      steps:
        - get_weather
        - save_trip_note
```

### State / artifact capture (verbatim from "Sessions, State, Plugins, And Artifacts")

```python
async def save_trip_note(city: str, summary: str, tool_context: ToolContext):
    artifact = types.Part.from_bytes(
        data=f"# Trip note for {city}\n\n{summary}\n".encode("utf-8"),
        mime_type="text/markdown",
    )
    await tool_context.save_artifact(filename=f"{city}-trip-note.md", artifact=artifact)
    tool_context.state["last_saved_artifact"] = f"{city}-trip-note.md"
```

Provider payload returned to promptfoo (verbatim JSON):

```json
{
  "artifact_names": ["london-trip-note.md"],
  "plugin_events": ["before_run:...", "after_run:..."],
  "session_state": {
    "callback_invocations": 3,
    "last_city": "London",
    "last_saved_artifact": "london-trip-note.md"
  }
}
```

### Workflow agent (verbatim from "Workflow Agents")

```python
weather_lookup_agent = Agent(
    name="weather_lookup_agent",
    model=model,
    tools=[get_weather],
    output_key="weather_snapshot",  # writes the final response to session state
)
briefing_agent = Agent(name="briefing_agent", model=model, instruction="Use weather_snapshot...")
workflow = SequentialAgent(
    name="trip_planning_workflow",
    sub_agents=[weather_lookup_agent, briefing_agent],
)
```

### Feature → assertion mapping (verbatim table from "Structured Outputs, Memory, And Advanced Tools")

| ADK feature | Assertion to add |
| --- | --- |
| `output_schema` or `output_key` | `is-json` with a JSON schema in `value`, plus `contains` on returned state |
| `MemoryService` | paired test cases that share a session id vs use distinct ones |
| MCP, OpenAPI, or authenticated tools | `trajectory:tool-used`, `trajectory:tool-args-match`, `is-refusal` |
| code executors | `trace-span-count` on `execute_tool *` plus safety `contains` / `regex` |
| multi-agent trees | one `trace-span-count` per `invoke_agent <name>` you require |
| long-running / resumable apps | `contains` on `session_state` snapshots before and after resume |

### Production notes (verbatim bullets from "Production Notes")

```
- Keep the provider span small. ADK emits the framework spans; the wrapper only has to preserve Promptfoo's parent trace and flush before the worker exits.
- The bundled example uses in-memory services so runs are deterministic. Swap in your real `SessionService`, `ArtifactService`, or `MemoryService` when persistence is part of the behavior under test.
- Reach for state and artifact assertions first; reserve model-graded assertions for outcomes that actually require semantics (tone, factuality, refusal quality).
- The optional LiteLLM adapter adds provider dependencies. Install it only when you need provider-prefixed model strings (`openai/...`, `anthropic/...`), and expect upstream warnings unrelated to your eval.
```

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- **Dismissed — no eval-harness / ADK overlap**:
  `docs-google-sre-reliable-product-launches.md` (Google launch-process
  discipline; no LLM-eval content); `docs-promptfoo-enterprise-guardrails.md`
  (runtime guardrail HTTP enforcement contract — a deployment-time defense, not
  eval provider wiring); `docs-promptfoo-enterprise-findings-reports.md`
  (post-scan finding disposition / export matrix — the reporting layer, not the
  eval surface); `docs-promptfoo-llm-rubric.md` (config reference for the
  model-graded `llm-rubric` family; this page only *defers* to model-graded
  assertions for semantics (Claim 11) and does not re-derive them);
  `docs-google-sre-team-lifecycles.md` (SRE org/lifecycles);
  `docs-google-sre-creating-production-launch-plan.md` (launch planning);
  `docs-google-sre-eliminating-toil.md` (toil measurement);
  `docs-litellm-batches-api.md` (LiteLLM batch rate-limit accounting — the page
  mentions the optional LiteLLM *adapter* only tangentially, no accounting
  overlap); `blog-pagerduty-sre-agent-triage.md` (AI incident triage — agent
  operations, not agent eval); `docs-langfuse-mcp-server.md` (docs MCP server —
  unrelated vendor). None touch wrapping an in-process agent framework behind a
  promptfoo provider, state/artifact assertion, or OTel span normalization.

### Cross-references with existing source notes

- **Corroborates**:
  - `docs-promptfoo-evaluate-crewai.md` **Claims 1–2** — the sibling
    framework-integration page; both wrap a self-hosted agent behind a promptfoo
    provider so the harness can grade logic it does not host. CrewAI uses
    `file://./agent.py` + `call_api(prompt, options, context)`; ADK uses the
    in-process Python provider shape. Together they bound the "adapter for a
    local agent framework" family. (Verified: #1681 Claims 1, 2 ✓)
  - `docs-promptfoo-evaluate-coding-agents.md` **Claim 7** ("Assert the path when
    the path matters") and **Claim 9** ("The agent's output is its final text
    response describing what it did, not the file contents") — this page's whole
    premise (assert on in-process state/spans, not the reply text) is the ADK
    instance of the same discipline; its Claim 6 (`workingDir`/`workspaceDiff`
    assertion metadata) is the coding-agent analogue of this page's
    `artifact_names`/`session_state` payload. (Verified: #1680 Claims 6, 7, 9 ✓)
  - `docs-promptfoo-evaluate-coding-agents.md` **Claim 12** — structured output
    first (`is-json` vs `contains-json`); this page's feature table reuses
    `is-json`/`contains` for `output_schema`/`output_key` and its state
    assertions. (Verified: #1680 Claim 12 ✓)
  - `docs-promptfoo-deterministic-metrics.md` **Claim 12** ("Trajectory
    assertions require trace data ... throw an error when traces are
    unavailable") and **Claim 13** (`trace-error-spans` auto-detection across
    status codes / error attributes / OTel status conventions) — this page's
    `trace-span-count`/`trace-error-spans` usage (Claim 3) is the ADK binding of
    those primitives, and Claim 5's `traceparent`/OTLP plumbing is the mechanism
    that supplies the required trace data. (Verified: #1289 Claims 12, 13 ✓)
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` **Claim 6**
    ("Sub-agents use their own distinct names; they don't inherit from the
    parent.") and **Claim 12** (`<operation> <target>` span naming, e.g.
    `invoke_agent {agent_name}`, `execute_tool {tool_name}`) — the OTel GenAI
    span shapes this page asserts over (`invoke_agent weather_agent`,
    `execute_tool get_weather`) are the instrumentation-side contract these
    claims define. This page is the eval-side consumer of the same contract.
    (Verified: #— Claims 6, 12 ✓ — instrumentation note)
  - `docs-promptfoo-assertions-metrics.md` **Claim 11** (the hub page's
    `trace-span-count`/`trace-error-spans`/`skill-used`/`trajectory:*` family
    catalogue) and **Claim 10** (deterministic vs model-assisted split) — this
    page selects from that catalogue and follows its deterministic-first split
    (Claim 11 here). It does not re-derive it. (Verified: #1287 Claims 10, 11 ✓)

- **Contradicts**: None. This is first-party vendor documentation of one guide
  page and opposes no existing source-note claim. The nearest surface — the
  in-process-provider-vs-HTTP rule (Claims 1–2) vs the coding-agent page's
  per-provider runtime-boundary defaults — is a *different axis* (test scope, not
  safety posture), not a conflict. No contradiction issue filed; `CONTRADICTIONS.md`
  has no relevant open `C-NNN` entry.

- **Extends**:
  - `docs-promptfoo-evaluate-crewai.md` (#1681) — extends the framework-
    integration family with a *second* adapter shape: CrewAI's `file://` module
    vs ADK's in-process Python provider, and adds this page's two net-new pieces
    the CrewAI page lacks — the explicit **in-process-vs-HTTP eval-surface
    decision** (Claims 1–2) and the **feature→assertion mapping method**
    (Claim 7).
  - `docs-promptfoo-evaluate-coding-agents.md` (#1680) — extends the
    "inspect what happened, not what was said" thesis (that note's Claims 6, 9)
    from the file/workspace surface to the **agent-internal state/artifact**
    surface (Claim 6), and supplies a concrete version-coupling failure mode
    (Claim 9) that note's regression-gate checklist does not name.
  - `docs-promptfoo-deterministic-metrics.md` (#1289) — extends the
    trace/trajectory catalogue from a config reference into the ADK
    provider-consumer case: how a framework's native spans reach the assertions
    (Claims 4–5) and which feature earns which assertion (Claim 7).

- **Novel**:
  1. **First ADK binding in the corpus** — no existing `source-notes/` file or
     `guide/` chapter mentions Google ADK. (Verified by grep for `adk` across
     `source-notes/` and `guide/`.)
  2. **The in-process-provider-vs-HTTP eval-surface decision** (Claims 1–2) — a
     generalizable rule for choosing the eval surface, not an ADK detail.
  3. **The framework-feature → assertion mapping method** (Claim 7) — "what do I
     assert on when the agent framework has feature X?", a reusable derivation
     heuristic.
  4. **The framework-version-coupling hazard** (Claim 9) — an eval harness pinned
     to a framework's internal event schema breaks silently across a major
     version bump (ADK 1.x→2.x; `SequentialAgent`→`Workflow`).
  5. **Agent-internal state/artifact assertions from an in-process provider**
     (Claim 6) — `artifact_names` / `plugin_events` / `session_state` asserted
     with deterministic `contains`/`is-json`, no model grader.

## Guide Impact

- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: Add an eval-surface decision beside
  "Golden labels from historical incidents." The chapter currently covers
  trajectory replay of historical incidents but not harness mechanics or the
  provider-shape choice. Add: choose the eval surface by what must be observed —
  an **in-process provider** to assert agent-internal state, artifacts, and
  native OTel spans; the **HTTP app-server** shape only to validate the deployed
  contract (auth, request shape, status codes)
  [source: docs-promptfoo-evaluate-google-adk, Claims 1, 2] [settled]. Pair it
  with the feature→assertion mapping (Claim 7) as the "what do I assert on?"
  heuristic, and with the state/artifact-before-judge rule (Claim 11).
- **Chapter 03 — read/write capability boundary and sandboxing
  (`guide/03-runbooks-and-agents.md:140`)**: Cite the in-process provider's
  ability to read `session_state`/`artifact_names`/`plugin_events` (Claim 6) as
  the reason an eval can grade an agent's *actions* rather than its self-report,
  cross-linking `docs-promptfoo-evaluate-coding-agents.md` Claim 9.
- **Chapter 05 (LLM Ops Reliability) — release engineering / "Pin to a supported
  line; separate patching from line moves" (`guide/05-llm-ops-reliability.md:79`)
  and "A green eval is not evidence until you can name what it measured"
  (`:567`)**: Add the **framework-version-coupling hazard** (Claim 9): an eval
  pinned to a framework's internal event schema and span shapes can break
  silently across a major version bump — ADK 1.x→2.x changes persisted event
  schemas (`node_info`, `output`), custom execution overrides, and retry/emission
  ownership; 2.9.2 deprecates `SequentialAgent` in favour of `Workflow`. Recommend
  pinning the framework line alongside the eval and re-running the suite on any
  major bump. Note this connection is our synthesis, not the page's own claim.
- **Chapter 05 — "A gate that cannot fail is not a gate"
  (`guide/05-llm-ops-reliability.md:655`)**: State plainly, per Claim 13, that
  this source gives **harness mechanics only** — no thresholds, no baselines, no
  CI job — so a gate built from it must supply its own fail criteria and
  commit-triggered run (same caveat as `docs-promptfoo-evaluate-crewai.md`
  Claim 9).
- **Chapter 02 (Observability) — "Two vendors, one standard: OTel GenAI semantic
  conventions" (`guide/02-observability.md:55`)**: Add the eval-side consumer of
  the same span contract: ADK emits `invoke_agent <name>` / `execute_tool <tool>`
  with `gen_ai.tool.name` and arguments, and promptfoo normalizes them into
  trajectory steps with **no custom span translator** (Claims 4–5) — evidence
  that the OTel GenAI schema is now consumed by eval harnesses as well as
  observability vendors. Cross-link
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claims 6, 12.

## Extraction Notes

- Source read in full via WebFetch of the single page
  (https://www.promptfoo.dev/docs/guides/evaluate-google-adk). Footer: "Last
  updated on **Oct 13, 2026** by **Michael D'Angelo**"; no canonical first-
  published date, so `date_published` carries the last-updated date (same
  convention as the sibling `docs-promptfoo-*` notes).
- **Scope discipline (per the Prospector's "extract the delta, not the page")**:
  deliberately **not** re-derived here are the generic assertion primitives already
  owned by the sibling notes — the `trajectory:*` / `trace-*` catalogue
  (`docs-promptfoo-deterministic-metrics.md` Claims 11–13;
  `docs-promptfoo-assertions-metrics.md` Claim 11), the "assert the path" / coding-
  agent methodology (`docs-promptfoo-evaluate-coding-agents.md` Claim 7), the
  structured-output `is-json`/`contains-json` split (that note's Claim 12), and the
  model-graded grader semantics (`docs-promptfoo-model-graded-metrics.md`). This
  note extracts the ADK binding and the *delta* the page adds — the eval-surface
  decision, the feature→assertion mapping, the version-coupling hazard, and the
  state/artifact payload.
- **Sub-pages followed: none.** The page links to ADK's own docs
  (`adk.dev/2.0`, `/workflows/`, `/sessions/`, `/callbacks/`, `/artifacts/`,
  `/agents/`) and sibling promptfoo integration guides; the ADK links are
  framework reference material and the promptfoo siblings (CrewAI, LangGraph,
  OpenAI Assistants) are already mined or out of scope, so none was re-fetched
  per MINER.md §1 — the page reproduces the configs it needs inline. The ADK
  migration facts in Claim 9 are quoted from the page's own callout, not from
  `adk.dev`.
- Quotes were verified character-for-character against the fetched rendered
  page. Code blocks arrive as collapsed single lines after HTML extraction; line
  breaks were restored at code/config boundaries only (no wording changes), the
  same convention as the sibling promptfoo config notes. The feature→assertion
  table was copied row-for-row.
- **Cross-ref verification (§4b)**: every cited claim number was located in the
  cited note and its content checked against what it is cited for — CrewAI #1681
  Claims 1–2; coding-agents #1680 Claims 6, 7, 9, 12; deterministic-metrics #1289
  Claims 11–13; assertions-metrics #1287 Claims 10–11; honeycomb Claims 6, 12
  (instrumentation note). No claim numbers invented; no quotes attributed to
  other notes.
- **Contradiction scan**: none filed. The in-process-vs-HTTP rule (Claims 1–2)
  and the coding-agent page's per-provider runtime-boundary defaults are different
  axes (test scope vs safety posture), not conflicting claims; per MINER.md §4a
  this is a conditioning variable, not a contradiction. `CONTRADICTIONS.md` has no
  relevant open `C-NNN` entry.
- **Candidate handling**: all 10 paths from `miner-related-notes.md` were cited
  or explicitly dismissed by name in the Cross-References block (none cited
  directly; the relevant cross-refs were found by searching `source-notes/` for
  `trajectory:tool-used`, `trace-span-count`, `invoke_agent`, `adk eval`, etc.,
  per the Prospector's overlap list and MINER.md §4).
- `confidence_overall` = `emerging`: first-party vendor documentation is
  authoritative for the documented config, code, and span shapes (individual
  claims graded `settled` where they are direct documented facts), but the page is
  a single-example walkthrough with no metrics, no run results, and no CI content;
  the operational value (the eval-surface decision, the feature→assertion method,
  the version-coupling hazard) is our synthesis across the page and the corpus.
  Consistent with the sibling promptfoo notes.
- `registry/sources.json` and `registry/claims-index.json` were intentionally not
  edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
