---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-openai-agents-python
source_type: docs
title: "Promptfoo: Evaluate OpenAI Agents (Python SDK) — the TracingProcessor/OTLP Bridge, Sandbox-Agent and Skills Provider Surface, and the Cost-Accounting Gap"
author: "Promptfoo (vendor documentation; page by Michael D'Angelo)"
date_published: 2026-10-14
date_extracted: 2026-10-14
last_checked: 2026-10-14
status: current
confidence_overall: emerging
issue: "#1707"
---

# Promptfoo: Evaluate OpenAI Agents (Python SDK)

> The vendor recipe that closes the **producer side** of promptfoo's agent-trace
> contract: because the built-in `openai:agents:*` provider only targets the
> JavaScript `@openai/agents` SDK, the Python `openai-agents` app is wrapped as a
> Python provider, and a custom `TracingProcessor` parses the W3C `traceparent`
> promptfoo injects, converts SDK spans to OTLP JSON, and ships them to
> promptfoo's OTLP receiver — the instrumentation several existing notes name as
> the missing dependency for `trajectory:*` assertions. It also documents the
> `SandboxAgent`/`skills` provider surface, the deterministic assertions that fire
> against the resulting spans, and the explicit **cost gap** (no dollar `cost` is
> inferred on this path). It carries **no** CI gating, thresholds, or baselines.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Evaluate OpenAI
  Agents (Python SDK)", under Evals → Guides → Integrations; auto-discovered from
  the registered `promptfoo-docs` site-crawl seed). Single guide page, no
  sub-pages followed.
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor.
  First-party documentation of the product's own Python-provider and
  OpenAI-Agents SDK binding — the config, code, and span shapes are
  authoritative and directly checkable against an installed CLI, but
  vendor-positioned: no run results, no metrics, no independent validation, and
  the SDK binding is demonstrated only against the vendor's own scaffolded
  example (`init --example openai-agents`). The page footer credits Michael.
- **Scope**: Covers (1) the Quick Start scaffold, pinned versions, and the
  optional `PROMPTFOO_ENABLE_OTEL=true` parent span; (2) the four-step tracing
  bridge that transports OpenAI Agents SDK spans into promptfoo; (3) the
  `trajectory:*` / `trace-*` assertions used as the grading surface; (4)
  long-horizon multi-turn runs via `vars.steps_json` + a shared `SQLiteSession`;
  (5) `SandboxAgent` / `Manifest` / `SandboxRunConfig` and the credential-staging
  warning; (6) the Skills surface (`ShellTool` + `metadata.skillCalls`); (7) the
  experimental `codex_tool`; (8) two red-team configs; (9) multimodal input; and
  (10) the Telemetry / Trace Timeline listing. Does NOT cover: CI gating,
  thresholds, baseline comparison, regression suites, or findings triage/export.
- **Last updated**: the page footer reads "Last updated on **Oct 14, 2026** by
  **Michael**" (the triage comments saw Oct 13, 2026; the page moved within a
  day of extraction). No canonical first-published date, so `date_published`
  carries the last-updated date (same convention as the sibling `docs-promptfoo-*`
  notes).

## Extracted Claims

### Claim 1: The page exists because promptfoo's built-in `openai:agents:*` provider targets only the JavaScript `@openai/agents` SDK — the Python `openai-agents` SDK must be wrapped as a Python provider, which is what makes sessions, tools, and framework tracing controllable
- **Evidence**: The top-of-page `note` callout contrasting the built-in provider
  with the Python path, and the intro sentence stating what the Python-provider
  route buys.
- **Confidence**: settled (documented product boundary)
- **Quote**: "The built-in `openai:agents:*` provider is for the JavaScript `@openai/agents` SDK. For the Python SDK, use the Python provider path described here."
- **Quote**: "Use the Python `openai-agents` SDK with Promptfoo by wrapping your agent as a Python provider. This gives you full control over agent code, tools, sessions, and framework-specific tracing, while still letting Promptfoo score outputs and assert on the traced workflow."
- **Our assessment**: This is the framing fact the Prospector flagged: the
  corpus's existing provider-adapter material covers CrewAI (`file://`) and ADK
  (in-process provider) but has no OpenAI-Agents binding, and the vendor's own
  first-class provider stops at the JS SDK. The "full control over ... tracing"
  phrase is the load-bearing half — the Python provider exists here specifically
  to *emit spans*, not merely to return `{"output": ...}` (contrast the CrewAI
  sibling, whose adapter's job is the JSON output shape).

### Claim 2: Promptfoo's agent-path assertions depend on a four-step producer bridge — promptfoo injects a W3C `traceparent`, the provider parses it and installs a custom `TracingProcessor`, the processor converts SDK spans to OTLP JSON, and promptfoo ingests them for the Trace Timeline and `trajectory:*` assertions
- **Evidence**: The "How The Tracing Works" section: the opening two-sentence
  statement and its numbered four-step list.
- **Confidence**: settled (documented mechanism; the page reproduces the shape)
- **Quote**: "Promptfoo can only assert on tool paths if it receives the agent's internal spans. The example does that by installing a custom `TracingProcessor` for the OpenAI Agents SDK and exporting those spans to Promptfoo's OTLP receiver."
- **Quote**: "Promptfoo enables tracing and injects a W3C `traceparent` into the Python provider context."
- **Our assessment**: This is the note's central and genuinely new contribution:
  the **producer-side contract** that several consumer-side notes leave as an
  open dependency. `docs-promptfoo-assertions-metrics.md` Claim 11 catalogues the
  `trajectory:*`/`trace-*` family and `docs-promptfoo-deterministic-metrics.md`
  Claim 12 states the family throws when trace data is absent; this page supplies
  the concrete instrumentation that makes the trace data present. It is also the
  closest corpus analogue to the ADK page's W3C-`traceparent`/OTLP plumbing
  (`docs-promptfoo-evaluate-google-adk.md` Claim 5) — but where ADK emits
  conformant spans natively, here the bridge is *custom code the operator
  maintains*.

### Claim 3: Skipping the exporter does **not** hard-fail the eval — it silently degrades a trajectory eval to an output-only eval, because `trajectory:*` assertions "will not have the trace data they need"
- **Evidence**: The section's explicit consequence sentence immediately after the
  four-step list.
- **Confidence**: settled (documented consequence; directly checkable)
- **Quote**: "If you skip this exporter, Promptfoo will not see the SDK's tool and handoff spans, so `trajectory:*` assertions will not have the trace data they need."
- **Our assessment**: The Ch05-relevant silent-failure mode. It sits precisely on
  the tension already filed as open **#1307** (promptfoo missing-trace semantics:
  built-in `trace-*` assertions throw vs a custom-JS trace gate passing green when
  tracing is off). This page's phrasing is the *virtuous* half — it tells the
  operator the assertions will lack data — but it does not say whether the
  built-in `trajectory:*` asserts *throw* (per
  `docs-promptfoo-deterministic-metrics.md` Claim 12) or merely match nothing.
  Either way the guide lesson is the same: the eval's health is coupled to the
  bridge, and a green trajectory gate is only meaningful if the bridge is known to
  be live.

### Claim 4: Two encodings are accepted on this path because the bridge emits OTLP **JSON** while the optional Python OTel wrapper defaults to **protobuf** — an opt-in (`PROMPTFOO_ENABLE_OTEL=true`) adds a provider-level parent span the custom SDK spans inherit
- **Evidence**: The two sentences following the four-step list, on the
  mixed-encoding rationale and the `PROMPTFOO_ENABLE_OTEL` parent span.
- **Confidence**: settled (documented behavior and rationale)
- **Quote**: "The example config accepts both OTLP JSON and OTLP/protobuf because the SDK bridge emits JSON while the wrapper exporter uses protobuf by default."
- **Quote**: "If you also enable Promptfoo's Python OpenTelemetry wrapper instrumentation with `PROMPTFOO_ENABLE_OTEL=true`, the example will emit a provider-level Python span as well. The custom SDK spans will inherit that active OpenTelemetry span as their parent."
- **Our assessment**: The mixed-encoding sentence is the page's most concrete
  footgun: a team that assumes one wire format ("OTLP") can have a clean error
  from one exporter and a working ingest from the other, and the fix is a config
  acceptance rather than a code change. The parent-span sentence is the
  observability payoff — it is the same "one trace" property the ADK page states
  (`docs-promptfoo-evaluate-google-adk.md` Claim 5), achieved here by inheritance
  under an explicitly enabled wrapper rather than by framework-native emission.

### Claim 5: The bridge maps SDK-custom spans into named OTLP attributes (`sandbox.operation`, `command`, `process.exit.code`) and normalizes `exec_command` tool spans as command trajectory steps, including the experimental Codex tool's spans as `command` / `codex.command`
- **Evidence**: The closing paragraph of "How The Tracing Works" naming the
  bridge's attribute mappings and the Codex-tool alias.
- **Confidence**: settled (documented mapping)
- **Quote**: "The example bridge maps SDK custom spans into normal OTLP attributes such as `sandbox.operation`, `command`, and `process.exit.code`, while Promptfoo normalizes OpenAI Agents `exec_command` tool spans as command trajectory steps. The same mapping also exposes command spans emitted by the SDK's experimental Codex tool as `command` and `codex.command`."
- **Our assessment**: This is what makes the sandbox/skills assertions (Claims 6,
  9, 10) *deterministic* — the bridge is the translation layer that turns
  SDK-specific span names into the stable `command`/`tool exec_command` vocabulary
  the assertions pattern-match. It is the operator-owned counterpart to the
  producer span-naming contract documented from the instrumentation side at
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claims 2/12: where
  Honeycomb assumes a framework that names spans correctly, this page writes the
  adapater that makes a framework's spans conform.

### Claim 6: The trajectory/trace assertions are the grading surface, with concrete numeric thresholds shown — `trajectory:tool-used`, `trajectory:tool-args-match` (`mode: partial`), `trajectory:tool-sequence`, `trajectory:step-count` (`agent *`, `min: 3`), the no-errors gate `trace-error-spans` (`max_count: 0`), and `trace-span-count` for sandbox/command spans
- **Evidence**: The "Assertion Pattern" YAML block, the sandbox `assert` block and
  the skills `assert` block, and the `trajectory:goal-success` pointer.
- **Confidence**: settled (documented config; primitives already catalogued)
- **Quote**: "Use `trajectory:goal-success` when you want a judge model to decide whether the traced workflow actually completed the task, not just whether it hit the right tool path."
- **Our assessment**: A **reuse**, not new material — the assertion primitives are
  owned by `docs-promptfoo-assertions-metrics.md` Claim 11 and
  `docs-promptfoo-deterministic-metrics.md` Claims 11–13, and the "assert the
  path" methodology by `docs-promptfoo-evaluate-coding-agents.md` Claim 7. Extract
  the *producer-side* mechanism only; the value here is the concrete threshold
  shapes (`min: 3` agent spans, `min: 2` `tool exec_command`, `min: 1`
  `sandbox.start`, `max_count: 0` errors) as worked examples, not the assertion
  types. `trajectory:goal-success` is model-judged and inherits the
  judge-variance caveats.

### Claim 7: Long-horizon tasks are encoded as one eval row — `vars.steps_json` is a JSON-encoded list of user turns executed sequentially against a shared `SQLiteSession`, and the provider returns `tokenUsage.numRequests`, cached-input tokens, and reasoning-token detail so the multi-call footprint is preserved
- **Evidence**: The "Long-Horizon Tasks" section's two paragraphs and the four
  bullets of what the pattern is useful for.
- **Confidence**: settled (documented code/config)
- **Quote**: "The example turns one eval row into a long-horizon task by passing a JSON-encoded list of user turns in `vars.steps_json`. The provider parses that JSON and executes the turns sequentially against a shared `SQLiteSession`, which lets the SDK preserve working memory across turns inside a single Promptfoo test case."
- **Quote**: "The example also returns `tokenUsage.numRequests`, cached-input tokens, and reasoning-token detail from the SDK's raw model responses. That preserves the real multi-call footprint of handoffs and tool/model loops instead of collapsing every eval row to one request."
- **Our assessment**: The reusable pattern is "one test case can be a whole
  conversation, not one request" — it is the eval-harness answer to the guide's
  recurring "the transcript is not the trajectory" theme (coding-agents Claim 9,
  ADK Claim 6). The explicit `numRequests` return matters for token accounting: a
  handoff-heavy row is *not* one model call, and an eval report that assumes one
  request per row under-counts the run.

### Claim 8: Promptfoo does **not** infer a dollar `cost` for this path, and the vendor's guidance is to return `cost` from the provider only when every billed model and hosted tool can be accounted for
- **Evidence**: The closing paragraph of "Long-Horizon Tasks".
- **Confidence**: settled (documented limitation + stated reason)
- **Quote**: "Promptfoo does not infer a dollar `cost` for this path automatically. A Python provider can mix models, hosted tools, and custom backends inside one agent graph, while the SDK's aggregate usage objects do not identify the priced model for each request. Return `cost` from your provider only when you can account for every billed model and hosted tool used by the run."
- **Our assessment**: The Ch05 cost-accounting gap, and the most guide-actionable
  negative finding on the page: an agent eval harness on a self-hosted Python
  provider can report **zero/absent cost by default**, so a cost regression gate
  built on promptfoo here silently measures nothing unless the provider is
  instrumented to return `cost`. This is the same "a green gate may verify
  nothing" family as `docs-promptfoo-assertions-metrics.md` Claims 3/4 and the
  caching note; the guide should pair it with those when the gate is a cost gate.
  Note the vendor names the *reason* (aggregate SDK usage does not identify the
  priced model per request) — i.e. the limitation is architectural, not a missing
  feature toggle.

### Claim 9: The sandbox provider surface is `SandboxAgent` / `Manifest` / `SandboxRunConfig` (SDK 0.14) with `UnixLocalSandboxClient` vs `DockerSandboxClient`, and the vendor's ops warning is to keep credentials and secrets out of staged `Manifest` files unless the backend and trace-redaction policy are appropriate
- **Evidence**: The "Sandbox Agents" section's introduction, the Python
  `SandboxAgent` example, the sandbox `assert` block, and the client-selection
  sentence plus credential warning.
- **Confidence**: settled (documented code/config and vendor guidance)
- **Quote**: "Use `UnixLocalSandboxClient` for local development, `DockerSandboxClient` when you need container isolation, and hosted sandbox clients when your application already depends on managed execution. Keep credentials and secrets out of staged `Manifest` files unless the sandbox backend and trace redaction policy are appropriate for that data."
- **Our assessment**: The Ch06-relevant new surface. Two operational points:
  (a) the client choice is the eval's *isolation* dial — a local client runs shell
  on the host, a Docker client contains it — and is thus the same layered-defaults
  mental model as the coding-agent workspace ("keeps calls from affecting each
  other, but it isn't a sandbox", coding-agents Claim 5); (b) the credential
  warning is a concrete secrets-in-artifact risk: staging a `Manifest` can commit
  secret material into an eval fixture *and* into spans if redaction is not
  configured. That pairs directly with the practitioner counterweight in
  `blog-linsun-sandboxing-agent-not-enough.md` (sandboxing answers "can it
  escape?", not "should it run?") — a local sandbox client is precisely the case
  where isolation is a configuration, not a guarantee.

### Claim 10: There is no first-class `skill-used` event for the Python Skills binding — the guidance is to assert the observable workflow (skill file read, helper command ran cleanly, answer reflects the result) or return `metadata.skillCalls` from the provider and use promptfoo's `skill-used` assertion
- **Evidence**: The "Skills" section: the mount example, the `assert` block, and
  the explicit no-first-class-event paragraph.
- **Confidence**: settled (documented limitation + workaround)
- **Quote**: "Today, the Python SDK does not expose a first-class skill invocation event that Promptfoo can normalize into `skill-used`. For Python SDK skill evals, assert on the observable workflow instead: the skill file was read, the helper command ran cleanly, and the final answer reflects the skill's result."
- **Our assessment**: A worked instance of "assert the observable effect when the
  framework does not surface the semantic event" — the same substitution the ADK
  page makes for state/artifacts (`docs-promptfoo-evaluate-google-adk.md` Claim 6).
  The `metadata.skillCalls` fallback is notable because it makes the eval
  contract *the provider's responsibility*: the operator must emit the signal the
  assertion reads, or the assertion has nothing to grade. That is the producer/
  consumer coupling the page keeps repeating.

### Claim 11: The experimental `codex_tool` lets a Python SDK agent delegate a bounded workspace task to Codex, and its command spans surface via the bridge — but if Codex itself is the system under test the vendor points to the dedicated `openai:codex-sdk` / `openai:codex-app-server` providers
- **Evidence**: The "Experimental Codex Tool" section's introduction, its Python
  example, and the closing "if Codex itself is the system under test" paragraph.
- **Confidence**: settled (documented guidance)
- **Quote**: "The Python SDK's Codex integration is available as `codex_tool` from `agents.extensions.experimental.codex`. It lets a regular Python SDK agent delegate a bounded workspace task to Codex during a tool call"
- **Quote**: "If Codex itself is the system under test, prefer Promptfoo's dedicated `openai:codex-sdk` or `openai:codex-app-server` providers. The app-server provider supports `approvals_reviewer: auto_review` (`guardian_subagent` remains a legacy alias); the Python `openai-agents` SDK 0.22.3 package does not expose a public automatic-review API."
- **Our assessment**: The self-limiting boundary is the extractable part: the
  vendor says the Python-provider path is for evaluating *your* agent that happens
  to call Codex, not for evaluating Codex itself — and notes the version-floor
  fact (SDK 0.22.3 exposes no public automatic-review API). For the guide this is
  a harness-selection rule of the same shape as the ADK page's `adk eval` vs
  promptfoo boundary (its Claim 12): use the framework's native surface when the
  framework *is* the thing under test.

### Claim 12: Two red-team configs ship — one for the Python SDK airline agent, one for the `SandboxAgent` coding workflow (prompt injection, secret reads, sandbox escapes, network egress, delayed CI exfiltration, verifier sabotage) — and generated tests inherit trace assertions, so internal tool-path failures surface even when the final answer looks like a refusal
- **Evidence**: The "Red Team The Agent" section: the config descriptions, the
  four CLI commands, the trace-inheritance sentence with the `update_seat`
  example, and the "not production-hardened" caveat.
- **Confidence**: settled for the documented config; emerging for the
  operational claim (vendor-positioned, no run results)
- **Quote**: "The target returns only the user-visible final answer, but each generated test inherits trace assertions so you can catch internal tool-path failures even when the final answer looks like a refusal. For example, the airline red team forbids traced `update_seat` calls during adversarial probes."
- **Quote**: "This sample is not production-hardened, so useful red-team runs should find some real breaks."
- **Our assessment**: The trace-inheritance property is the notable bit — it fuses
  the red-team surface with the trajectory grader, so a refusal-shaped output with
  a forbidden internal tool call is caught rather than passed. The strategies are
  deliberately narrow (`jailbreak:meta` / `jailbreak:hydra` only), and the
  "not production-hardened" line is the vendor's own honesty about the sample.
  Cross-link the Ch06 red-team material: this page performs the runs **manually**
  (below, Claim 14), so it is harness wiring, not a CI gate.

### Claim 13: The Python provider also passes structured multimodal input through `Runner.run_sync()`, and the encoding diverges from the JS SDK — Python uses `image_url` where the JavaScript examples use `image`
- **Evidence**: The "Multimodal Input" section's Python example and its closing
  sentence.
- **Confidence**: settled (documented code + divergence)
- **Quote**: "The Python provider runs your own function, so you can pass structured multimodal input directly to `Runner.run_sync()` instead of a plain string"
- **Quote**: "Python SDK image input items use `image_url`; the JavaScript SDK examples use `image`."
- **Our assessment**: A small but concrete cross-SDK portability trap worth a
  footnote: a reader following a JavaScript example under the Python provider gets
  a silently different input schema. It reinforces Claim 1's boundary — the two
  SDKs are not interchangeable, and the Python path is maintained by the operator.

### Claim 14 (explicit gap): The page contains **no** CI gating — eval and red-team runs are manual `npx promptfoo@latest eval` / `redteam` commands, with no pipeline file, threshold, baseline comparison, or commit-triggered run anywhere
- **Evidence**: Every execution step is an interactive CLI call (Quick Start, the
  red-team commands, and `npx promptfoo@latest view`); no workflow/CI file,
  threshold, or baseline appears on the page. The Prospector flagged the same gap.
- **Confidence**: settled (absence — verified by reading the full page)
- **Quote**: "npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache"
- **Our assessment**: The anti-over-claim to preserve. Any guide framing of this
  page as an eval *gate* would be an extrapolation it does not support. It
  demonstrates harness *mechanics* (provider shape, trace bridge, span
  normalization, assertion patterns, red-team configs), not eval-in-CI *practice*.
  Same gap as the CrewAI sibling (`docs-promptfoo-evaluate-crewai.md` Claim 9) and
  the ADK sibling (`docs-promptfoo-evaluate-google-adk.md` Claim 13).

## Concrete Artifacts

All artifacts copied from
https://www.promptfoo.dev/docs/guides/evaluate-openai-agents-python (sections
named). Code blocks arrive as collapsed single lines after HTML extraction; line
breaks were restored at code/config/YAML boundaries only, with no wording
changes. Prose quotes elsewhere in this note are character-for-character from the
rendered page (markdown link syntax reduced to its rendered text).

### Quick Start (verbatim from "Quick Start")

```
npx promptfoo@latest init --example openai-agents
cd openai-agents
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export OPENAI_API_KEY=your_api_key_here
# Run the eval
npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache
# Optional: also emit a provider-level Python OpenTelemetry span
python -m pip install "opentelemetry-api>=1.44,<2" "opentelemetry-sdk>=1.44,<2" "opentelemetry-exporter-otlp-proto-http>=1.44,<2"
PROMPTFOO_ENABLE_OTEL=true npx promptfoo@latest eval -c promptfooconfig.yaml --no-cache
npx promptfoo@latest view
```

Pinned requirements (verbatim from "Quick Start" prose): "The example uses
OpenAI Agents SDK 0.22.x and requires Python 3.10 or later. The sandbox and skill
scenarios run local shell commands and require macOS/Linux or WSL."

### The four-step tracing pipeline (verbatim from "How The Tracing Works")

```
1. Promptfoo enables tracing and injects a W3C `traceparent` into the Python provider context.
2. The example parses that trace context and configures a custom OpenAI Agents tracing processor.
3. The processor converts OpenAI Agents spans into OTLP JSON.
4. Promptfoo ingests those spans and makes them available in the Trace Timeline and `trajectory:*` assertions.
```

### What the example covers (verbatim bullets from "What The Example Covers")

```
- multi-turn execution over a persistent `SQLiteSession`
- SDK `SandboxAgent` execution over a staged Unix-local Python workspace
- local-shell skill mounting with `ShellTool(environment={"type": "local", "skills": [...]})`
- specialist handoffs between a triage agent, an FAQ agent, and a seat-booking agent
- Promptfoo trace ingestion of the SDK's internal spans
- assertions on tool usage, tool arguments, sandbox commands, agent spans, tool order, and overall task success
```

### Assertion pattern (verbatim YAML from "Assertion Pattern")

```yaml
vars:
  steps_json: |
    [
      "My name is Ada Lovelace and my confirmation number is ABC123.",
      "Move me to seat 14C.",
      "Also, what is the baggage allowance?"
    ]
assert:
  - type: trajectory:tool-used
    value:
      - lookup_reservation
      - update_seat
      - faq_lookup
  - type: trajectory:tool-args-match
    value:
      name: update_seat
      args:
        confirmation_number: ABC123
        new_seat: 14C
      mode: partial
  - type: trajectory:tool-sequence
    value:
      steps:
        - lookup_reservation
        - update_seat
        - faq_lookup
  - type: trajectory:step-count
    value:
      type: span
      pattern: 'agent *'
      min: 3
  - type: trace-error-spans
    value:
      max_count: 0
```

### Sandbox agent (verbatim Python from "Sandbox Agents")

```python
from agents import ModelSettings, Runner
from agents.run import RunConfig
from agents.sandbox import Manifest, SandboxAgent, SandboxRunConfig
from agents.sandbox.entries import File
from agents.sandbox.sandboxes.unix_local import UnixLocalSandboxClient
agent = SandboxAgent(
    name="Workspace analyst",
    model="gpt-5.4-mini",
    instructions="Inspect the workspace with shell before answering.",
    default_manifest=Manifest(
        entries={
            "repo/task.md": File(content=b"Find the high-severity issue."),
        }
    ),
    model_settings=ModelSettings(include_usage=True),
)
result = Runner.run_sync(
    agent,
    "Inspect the staged repo and summarize the issue.",
    run_config=RunConfig(
        sandbox=SandboxRunConfig(client=UnixLocalSandboxClient()),
    ),
)
```

Sandbox test assertions (verbatim YAML from "Sandbox Agents"):

```yaml
assert:
  - type: trace-span-count
    value:
      pattern: tool exec_command
      min: 2
  - type: trace-span-count
    value:
      pattern: sandbox.start
      min: 1
  - type: trace-span-count
    value:
      pattern: response *
      min: 2
  - type: trajectory:step-count
    value:
      type: command
      pattern: '*unittest*'
      min: 1
```

### Skills assertions (verbatim YAML from "Skills")

```yaml
assert:
  - type: trajectory:step-count
    value:
      type: command
      pattern: '*discount-review/SKILL.md*'
      min: 1
  - type: trajectory:step-count
    value:
      type: command
      pattern: '*analyze_discount_policy.py*'
      min: 1
  - type: contains
    value: return discount_percent >= 20
  - type: not-contains
    value: 'stderr:'
```

### Telemetry / Trace Timeline (verbatim bullets from "Telemetry")

```
- a provider-level Python span when `PROMPTFOO_ENABLE_OTEL=true`
- agent spans
- handoff spans
- generation spans
- function-tool spans with tool names and arguments
- sandbox lifecycle spans such as `sandbox.start` and `sandbox.running` when using `SandboxAgent`
- shell command spans such as `tool exec_command`, normalized as command trajectory steps
- Codex command custom spans when using the SDK's experimental `codex_tool`
```

"The same trace data powers `trace-span-*` and `trajectory:*` assertions."
(verbatim closing sentence of "Telemetry").

## Cross-References

### Candidate paths from `miner-related-notes.md` (10 paths — cited or dismissed before writing)

- `source-notes/docs-promptfoo-evaluate-coding-agents.md` — **cited**
  (Corroborates Claims 5, 7; Extends). Closest sibling; owns trajectory-path
  methodology, workspace isolation, and the "isn't a sandbox" limit.
- `source-notes/docs-litellm-batches-api.md` — batch rate-limit accounting; no
  eval-provider or tracing surface. **Dismissed.**
- `source-notes/docs-promptfoo-enterprise-findings-reports.md` — post-scan
  finding disposition / export matrix; the reporting layer, not the eval surface.
  **Dismissed.**
- `source-notes/docs-langfuse-mcp-server.md` — Langfuse docs MCP server;
  unrelated vendor. **Dismissed.**
- `source-notes/blog-promptfoo-owasp-red-teaming.md` — **cited** (Corroborates
  Claim 4: pre-deployment red teaming integrated into CI/CD on a recurring
  schedule — the discipline this page's manual red-team runs do not satisfy).
- `source-notes/docs-promptfoo-enterprise-guardrails.md` — runtime guardrail HTTP
  enforcement contract (deployment-time defense, not eval provider wiring).
  **Dismissed.**
- `source-notes/docs-promptfoo-evaluate-google-adk.md` — **cited**
  (Corroborates Claim 5; Extends). The framework-binding sibling: same
  `traceparent`/OTLP mechanism, but ADK emits conformant spans with no custom
  translator while this page is the custom-translator case.
- `source-notes/blog-pagerduty-sre-agent-triage.md` — PagerDuty SRE-agent
  incident triage; agent *operations*, not agent *eval*. **Dismissed.**
- `source-notes/docs-promptfoo-pi-scorer.md` — external model-graded scorer; no
  provider-instrumentation or tracing overlap. **Dismissed.**
- `source-notes/docs-google-sre-team-lifecycles.md` — SRE team org/lifecycles; no
  LLM-eval content. **Dismissed.**

### Cross-references with existing source notes

- **Corroborates**:
  - `docs-promptfoo-deterministic-metrics.md` **Claim 12** ("Trajectory
    assertions require trace data. Enable tracing for the eval and use a provider
    that emits tool-oriented spans or attributes." and "If trace data is not
    available, the assertion will throw an error rather than failing...") — this
    page is the *producer-side* of that documented dependency: install the
    `TracingProcessor`, parse the injected `traceparent`, export OTLP JSON so the
    trace data exists. (Verified: #1289 Claim 12, read in full.)
  - `docs-promptfoo-assertions-metrics.md` **Claim 11** — the hub page catalogues
    the `trace-span-count` / `trace-error-spans` / `skill-used` / `trajectory:*`
    family this page *uses* as its grading surface; this page does not re-derive
    the types. (Verified: #1287 Claim 11, read in full.)
  - `docs-promptfoo-evaluate-coding-agents.md` **Claim 7** ("**Assert the path
    when the path matters.** If the requirement is "ran tests," "asked for
    approval," or "used the MCP tool," do not rely only on the final answer.") —
    the methodology this page's trajectory asserts instantiate for the OpenAI
    Agents Python path. (Verified: #1680 Claim 7.)
  - `docs-promptfoo-evaluate-coding-agents.md` **Claim 5** ("A workspace keeps
    calls from affecting each other, but it isn't a sandbox. An agent with shell
    access can still reach the rest of the file system, so run untrusted agents in
    a container.") — the isolation mental model behind this page's
    `UnixLocalSandboxClient` vs `DockerSandboxClient` choice (Claim 9).
    (Verified: #1680 Claim 5.)
  - `docs-promptfoo-evaluate-google-adk.md` **Claim 5** ("The example provider
    preserves Promptfoo's W3C `traceparent`, starts a small provider span beneath
    it, and exports ADK's child spans to Promptfoo's built-in OTLP receiver.") —
    the same W3C-`traceparent` + OTLP-receiver mechanism, here implemented by a
    custom translator rather than by a framework's native emission. (Verified:
    #1694 Claim 5.)
  - `docs-promptfoo-evaluate-crewai.md` **Claims 1–2** — the sibling framework
    integration page; both wrap a self-hosted agent behind a Python provider
    (`file://./agent.py` + `call_api` there; the in-process Python provider here).
    Together they bound the "adapter for a local agent framework" family. (Verified:
    #1681 Claims 1, 2.)
  - `blog-promptfoo-owasp-red-teaming.md` **Claim 4** — "Pre-deployment red
    teaming must be integrated into CI/CD pipelines and run on a recurring
    schedule"; this page ships red-team configs but runs them manually (Claim 14),
    so it demonstrates the config shape, not the CI discipline. (Verified: #555
    Claim 4.)

- **Contradicts**: None. This is first-party vendor documentation of one guide
  page and opposes no existing source-note claim. Checked `CONTRADICTIONS.md`
  (no open `C-NNN` entries) and open `contradiction`-labeled issues. The nearest
  surface, open **#1307** (promptfoo missing-trace semantics: built-in trace-*
  assertions throw vs a custom-JS trace gate passing green when tracing is off),
  is a *sibling* distinction, not a conflict: this page's caution that skipping
  the exporter leaves `trajectory:*` without data sits on the same "the gate's
  health is coupled to the trace pipeline" family documented at
  `docs-promptfoo-deterministic-metrics.md` Claim 12, rather than opposing it. No
  contradiction issue filed.

- **Extends**:
  - `docs-promptfoo-evaluate-coding-agents.md` (#1680) — extends the
    coding-agent eval methodology from the *consumer* side (workspace,
    trajectory asserts, "isn't a sandbox") to the *producer* side: the
    `TracingProcessor`/OTLP bridge that supplies the spans those asserts read
    (Claims 2–5), plus a Python-provider-specific cost gap (Claim 8) that note's
    regression-gate checklist does not name.
  - `docs-promptfoo-evaluate-google-adk.md` (#1694) — extends the
    framework-integration family with the *contrasting* adapter shape: ADK emits
    conformant OTel GenAI spans and needs "no custom span translator" (its Claim
    4), whereas the OpenAI Agents Python SDK needs a hand-written bridge
    (`TracingProcessor` + OTLP JSON). The pair bounds "framework emits spans natively"
    vs "operator writes the exporter."
  - `docs-promptfoo-evaluate-crewai.md` (#1681) — extends the self-hosted
    Python-provider pattern from "return `{"output": ...}`" to "return output
    *and* emit spans"; this page's provider exists to feed a trajectory grader,
    not merely to shape the output.
  - `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` — extends the
    producer span-naming/attribution contract (Claims 2, 6, 12:
    `gen_ai.conversation.id`/`agent.name`/`operation.name`, distinct sub-agent
    names, `<operation> <target>` naming) with an operator-written bridge that
    maps a specific framework's spans onto promptfoo-normalizable attributes
    (`sandbox.operation`, `command`, `process.exit.code`) — the adapter layer that
    sits between a framework and the contract the assertions assume.
  - `blog-linsun-sandboxing-agent-not-enough.md` — extends the "sandboxing is
    necessary, but not sufficient" line to the eval-fixture case: this page's
    local sandbox client and `Manifest` credential-staging warning (Claim 9) show
    that an eval sandbox is a configuration, not a guarantee, and that staged
    manifests are an artifact-hygiene surface.

- **Novel**: First corpus coverage of the **OpenAI Agents Python SDK** binding and
  the **producer-side trace bridge** (grep confirmed zero prior `source-notes/`
  hits for `openai-agents` / `TracingProcessor`). Specifically new:
  1. **The custom `TracingProcessor` / OTLP-JSON bridge** that converts SDK spans
     into promptfoo-ingestible traces, parsing the injected W3C `traceparent`
     (Claims 2, 4) — the instrumentation the corpus's consumer-side notes name as
     a dependency.
  2. **The silent under-assertion consequence** of skipping the exporter (Claim
     3) — a trajectory eval degrades to an output-only eval.
  3. **The SDK-custom-span → OTLP attribute mapping** (`sandbox.operation`,
     `command`, `process.exit.code`; `exec_command` normalized as command steps;
     `codex.command`) (Claim 5).
  4. **The `SandboxAgent` / `Manifest` / `SandboxRunConfig` provider surface** and
     its credential-staging warning (Claim 9).
  5. **The Skills no-first-class-event limitation** and the
     `metadata.skillCalls`/observable-workflow workaround (Claim 10).
  6. **The explicit cost-accounting gap** — no automatic dollar `cost` on this
     path and the accounting rule for returning it (Claim 8).
  7. **The long-horizon `vars.steps_json` + shared `SQLiteSession` pattern** with
     `numRequests`/cached-input/reasoning-token returns (Claim 7).

## Guide Impact

- **Chapter 02 (Observability) — OTel GenAI span conventions
  (`guide/02-observability.md:55`)**: Add the **producer-side bridge** as the
  eval-harness consumer of the same span contract: promptfoo injects a W3C
  `traceparent`, a custom `TracingProcessor` converts OpenAI Agents SDK spans to
  OTLP JSON, and the SDK's `exec_command` tool spans are normalized into command
  trajectory steps (Claims 2–5). State the mixed-encoding footgun — OTLP JSON
  from the SDK bridge vs protobuf from the OTel wrapper (Claim 4) — and the
  silent-degradation rule: skipping the exporter means `trajectory:*` assertions
  "will not have the trace data they need" (Claim 3). Cross-link
  `docs-promptfoo-deterministic-metrics.md` Claim 12 and
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` Claims 2/12.
- **Chapter 05 (LLM Ops Reliability) — "A green eval is not evidence until you
  can name what it measured" (`guide/05-llm-ops-reliability.md:567`) and "A gate
  that cannot fail is not a gate" (`:655`)**: Add the **cost-accounting gap**
  (Claim 8): an agent eval on a self-hosted Python provider does not get an
  automatic dollar `cost`, so a cost regression gate on this path measures nothing
  unless the provider returns `cost` — pair with the "cannot-fail gate" family
  (`docs-promptfoo-assertions-metrics.md` Claims 3/4). Also record that this
  source gives **harness mechanics only** — no thresholds, baselines, or CI job
  (Claim 14) — so a gate built from it must supply its own fail criteria and
  commit-triggered run (same caveat as `docs-promptfoo-evaluate-crewai.md` Claim 9
  and `docs-promptfoo-evaluate-google-adk.md` Claim 13).
- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: Add the **long-horizon single-row
  pattern**: one eval row can be a whole conversation via `vars.steps_json`
  against a shared `SQLiteSession` (Claim 7), so an eval can grade memory-dependent
  workflows, handoffs over time, and tool-usage regressions. Pair with the
  trajectory-assertion grading surface (Claim 6) and the provider-adapter
  contract (Claim 1) as the mechanism for exercising a self-hosted agent under an
  eval harness without instrumenting the framework itself.
- **Chapter 06 (Security and Trust) — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`)**: Add the **sandbox/credential-staging
  warning** (Claim 9): keep credentials and secrets out of staged `Manifest`
  files unless the sandbox backend and trace-redaction policy are appropriate;
  choose `DockerSandboxClient` (container isolation) over `UnixLocalSandboxClient`
  for untrusted agents, since a local sandbox client runs on the host. Cite the
  coding/sandbox **red-team config shape** (Claim 12) — generated tests inherit
  trace assertions, catching internal tool-path failures even when the answer
  looks like a refusal — and carry the honest caveats: strategies limited to
  `jailbreak:meta`/`jailbreak:hydra`, runs are manual (Claim 14), and the sample
  is "not production-hardened" (Claim 12). Cross-link
  `blog-linsun-sandboxing-agent-not-enough.md` (sandboxing is necessary, not
  sufficient).

## Extraction Notes

- Source read in full via WebFetch of the single page
  (https://www.promptfoo.dev/docs/guides/evaluate-openai-agents-python). Footer:
  "Last updated on **Oct 14, 2026** by **Michael**"; the Prospector triage
  (2026-10-13) saw the page dated Oct 13, 2026, so it was edited within a day
  before extraction, and `last_checked` is the extraction date (2026-10-14).
- **Scope discipline (per the Prospector's "extract the delta, not the page")**:
  deliberately **not** re-derived here are the generic assertion primitives already
  owned by the sibling notes — the full `trajectory:*` / `trace-*` catalogue
  (`docs-promptfoo-assertions-metrics.md` Claim 11;
  `docs-promptfoo-deterministic-metrics.md` Claims 11–13), the "assert the path"
  methodology (`docs-promptfoo-evaluate-coding-agents.md` Claim 7), the
  workspace-isolation model ("it isn't a sandbox", that note's Claim 5), and the
  self-hosted Python-provider adapter pattern
  (`docs-promptfoo-evaluate-crewai.md` Claims 1–2). This note extracts the
  **producer-side bridge**, the sandbox/skills provider surface, the red-team
  config shape, and the cost-accounting gap.
- **Sub-pages followed: none.** The page's outbound links are the Python-provider
  reference (`/docs/providers/python/`), the tracing docs (`/docs/tracing/`), and
  the JavaScript-SDK provider (`/docs/providers/openai-agents/`) — provider/config
  references or already-mined assertion material, so none was re-fetched per
  MINER.md §1; the page reproduces the configs and code it needs inline.
- Quotes were verified character-for-character against the fetched rendered page.
  Code blocks arrive as collapsed single lines after HTML extraction; line breaks
  were restored at code/config/YAML boundaries only (no wording changes), the same
  convention as the sibling promptfoo config/guide notes. Markdown link syntax
  inside quoted prose was reduced to its rendered text (e.g. "the built-in
  `openai:agents:*` provider"); no wording, punctuation, or clause order was
  altered, and no two non-adjacent sentences were spliced (MINER.md §2a).
- **Cross-ref verification (§4b)**: every cited claim number was located in the
  cited note and its content checked against what it is cited for —
  deterministic-metrics #1289 Claim 12; assertions-metrics #1287 Claim 11;
  coding-agents #1680 Claims 5, 7; google-adk #1694 Claim 5; crewai #1681 Claims
  1–2; owasp-red-teaming #555 Claim 4; honeycomb (instrumentation note) Claims 2,
  6, 12. No claim numbers invented; no quotes attributed to other notes.
- **Contradiction scan**: none filed. `CONTRADICTIONS.md` has no open `C-NNN`
  entries; `gh issue list --label contradiction --state open` returns 19 issues,
  none touching the OpenAI Agents Python binding, the OTLP bridge, sandbox
  clients, or this page's assertions. The nearest, **#1307** (missing-trace
  semantics), is a sibling distinction this page's Claim 3 sits on the same side
  of (trace-coupled gate health), not a conflict.
- **Candidate handling**: all 10 paths from `miner-related-notes.md` were cited or
  explicitly dismissed by name in the Cross-References block. The additional
  cited notes (`docs-promptfoo-evaluate-crewai.md`,
  `docs-promptfoo-deterministic-metrics.md`,
  `docs-promptfoo-assertions-metrics.md`,
  `blog-honeycomb-instrumenting-ai-agents-opentelemetry.md`,
  `blog-linsun-sandboxing-agent-not-enough.md`,
  `blog-promptfoo-owasp-red-teaming.md`) were found by searching `source-notes/`
  (`openai-agents`, `TracingProcessor`, `traceparent`, `trajectory:tool-used`,
  `sandbox`), per the Prospector's overlap list and MINER.md §4.
- `confidence_overall` = `emerging`: first-party vendor documentation is
  authoritative for the documented config, code, and span shapes (individual
  claims graded `settled` where they are direct documented facts), but the page is
  a single-example walkthrough with **no metrics, no run results, and no CI
  content**, and the SDK binding is demonstrated only against the vendor's own
  scaffolded example. The operational value (the producer-side bridge as the
  missing dependency for `trajectory:*` assertions, the cost gap, the
  sandbox/credential-staging risk) is our synthesis across the page and the
  surrounding corpus, consistent with the sibling promptfoo notes (#1680, #1681,
  #1694).
- `registry/sources.json` and `registry/claims-index.json` were intentionally not
  edited: they are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
