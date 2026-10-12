---
source_url: https://www.promptfoo.dev/docs/guides/evaluate-coding-agents
source_type: docs
title: "Promptfoo Guide: Evaluating Coding Agents — Capability Tiers, Workspace Isolation, and the Trajectory CI Gate"
author: "Promptfoo (vendor documentation; page by Roydon Sequeira)"
date_published: 2026-10-11
date_extracted: 2026-10-12
last_checked: 2026-10-12
status: current
confidence_overall: emerging
issue: "#1680"
---

# Promptfoo Guide: Evaluating Coding Agents

> The vendor's *agent-system eval methodology* guide — the case that an agent
> eval measures a system with emergent behavior rather than a function, the
> three-tier provider framing (text → coding-agent SDK → app-server) that scopes
> what is actually under test, the `copy_working_dir` workspace-isolation model
> (with its explicit "it isn't a sandbox" limit), the trajectory/approval
> assertions that grade the *path* a run took, and the cost/latency/non-determinism
> thresholds that make a coding-agent eval CI-gateable. Distinct from the
> existing promptfoo assertion-catalogue notes: this page is the operator's
> methodology for evaluating an agent as a system.

## Source Context

- **Type**: docs (vendor product documentation — promptfoo "Evaluate Coding
  Agents" guide page under `/docs/guides/`, discovered from the
  `promptfoo-docs` site-crawl seed)
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor
  (now part of OpenAI per the site banner); the page footer credits Roydon
  Sequeira. First-party documentation of the tool's own coding-agent providers
  and eval workflow — authoritative for what promptfoo does with a given
  config (which providers exist, what `copy_working_dir` does, which assertion
  metadata is emitted), but vendor-positioned: the page reports one illustrative
  cost band and no measured gate-failure-rate, flake-rate, or isolation-escape
  figures, and there is no independent practitioner validation. Every mechanism
  below is checkable against an installed CLI and the linked provider pages.
- **Scope**: A methodology guide for coding-agent evals: why agent evals differ
  from LLM evals, the three capability tiers, the provider/safety-posture
  selection table, four worked examples (security audit with structured output,
  app-server approval, refactor-with-test-verification, multi-file feature),
  isolated workspaces (`copy_working_dir`, `workingDir`/`workspaceDiff`), the
  evaluation techniques (structured output, cost/latency, non-determinism,
  LLM-as-judge), safety guidance, a QA/release checklist, and five evaluation
  principles. It deliberately does **not** re-derive the generic assertion
  primitives (that is the job of the sibling `docs-promptfoo-*` config pages);
  its payload is the *system-eval framing* and the coding-agent-specific
  mechanics. The linked per-provider reference pages were not followed (they are
  provider config references, not new methodology).
- **Last updated**: the page footer reads "Last updated on **Oct 11, 2026** by
  **Roydon Sequeira**"; page undated, so `date_published` carries the
  last-updated date.

## Extracted Claims

### Claim 1: An agent eval tests a *system with emergent behavior*, not a function, for three stated reasons — non-determinism compounds across tool calls, intermediate steps matter even when final outputs match, and capability is gated by architecture — so "you're evaluating the system, not just the model"
- **Evidence**: The "Why agent evals are different" section's opening
  contrast (chat model = one-step function; agent = decide/act/observe/iterate)
  and its three bolded reasons.
- **Confidence**: settled (documented framing; every example on the page
  operationalizes it)
- **Quote**: "Standard LLM evals test a function: given input X, does output Y meet criteria Z? Agent evals test a system with emergent behavior." and "**Non-determinism compounds.** A chat model's temperature affects one generation. An agent's temperature affects every tool call, every decision to read another file, every choice to retry. Small variations cascade." and "**Intermediate steps matter.** Two agents might produce identical final outputs, but one read 3 files and the other read 30. Cost, latency, and failure modes differ dramatically." and "**Capability is gated by architecture.** You can't prompt a plain LLM into reading files. The model might be identical, but the agent harness determines what's possible. This means you're evaluating the system, not just the model."
- **Our assessment**: This is the page's thesis and the reason it is worth a
  separate note: the corpus already has promptfoo's per-assertion config
  semantics but not the *scoping argument* for agent evals. The three reasons
  each map to a different existing guide concern — "non-determinism compounds"
  justifies `--repeat 3` (Claim 10), "intermediate steps matter" justifies
  trajectory assertions (Claim 7), and "capability gated by architecture" is
  what makes the LLM baseline a real control (Claim 2). Buy it as vendor framing;
  its operational teeth are in the claims that follow.

### Claim 2: Provider capability is tiered — Tier 0 text models, Tier 1 coding-agent SDKs (`openai:codex-sdk`, `anthropic:claude-agent-sdk`, `opencode:sdk`), Tier 2 rich client servers (`openai:codex-app-server`, `openinterpreter`) — and the *same underlying model* behaves differently at each tier, so a plain-LLM baseline proves file/shell/runtime access is contributing
- **Evidence**: The "Capability tiers" table (three rows, each with example
  providers, "use when" and "watch for" columns) and the paragraph after it.
- **Confidence**: settled (documented product taxonomy)
- **Quote**: "The same underlying model behaves differently at each tier. A plain `claude-sonnet-5` call can't read your files; wrap it in Claude Agent SDK and it can. Use a plain LLM baseline when you want to prove that file access, shell access, or runtime state is actually contributing to the result."
- **Our assessment**: The tier framing is the eval-scoping lens the Prospector
  asked for: it names *what is under test* as a configuration decision, not a
  marketing category. The practical rule the page draws from it — run a plain
  LLM baseline for any task that requires file or tool access — is a negative
  control that catches the failure mode where an eval silently grades the
  model's prose about doing the task rather than the doing of it (echoed in the
  security-audit example, Claim 12). This is a stronger statement than "use a
  baseline": the tier boundary is why the baseline is meaningful.

### Claim 3: Provider selection is a runtime-boundary decision with a per-provider default safety posture — Codex SDK (git repo check, filesystem sandbox, network/search off, minimal env), Codex app-server (read-only sandbox, approvals declined, ephemeral threads), Claude Agent SDK (no tools by default), and OpenCode SDK (temporary workspace, read-only tools) — and codex-desktop is only an alias that starts its own child process
- **Evidence**: The provider-selection table's "Runtime boundary" and "Default
  safety posture" columns, and the `codex-desktop` alias paragraph beneath it.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`openai:codex-desktop` is an alias for the app-server protocol provider. Promptfoo starts its own `codex app-server` child process; it does not attach to an already-running Codex Desktop app window or reuse Desktop UI state." and "Across the coding-agent providers, relative `working_dir` values resolve from the directory containing the config file. That keeps configs portable when you run the same eval from the example directory, the repo root, or CI."
- **Our assessment**: Two extractable operational facts. First, the safety
  posture is a *default per provider*, not a universal — teams evaluating the
  same task across providers are comparing different sandboxes, which is an
  experimental control to hold constant or explicitly vary. Second, the alias
  caveat is a reproducibility trap: `codex-desktop` reads as "use my Desktop
  app," but it spawns an independent child process with no shared UI/thread
  state, so a test that assumes it reuses a signed-in Desktop session will not
  behave as the name suggests. The `working_dir`-relative-to-config rule is the
  portability detail that keeps the same config valid from a laptop and CI.

### Claim 4: `copy_working_dir` gives each eval step an isolated workspace that is created before the call and deleted after its assertions run — `true` chooses clone-vs-copy automatically, `'git'` forces a clone of the current commit, `'copy'` forces a copy — and cloning requires Git 2.41 or newer
- **Evidence**: The "Isolated workspaces" section: the motivating sentence
  (an editing agent mutates `working_dir` for every later call), the
  supported-provider sentence, the value/semantics table, and the Git-version
  caveat.
- **Confidence**: settled (documented product behavior)
- **Quote**: "An agent that edits files changes `working_dir` for every test, repeat, and concurrent call that comes after it. Set `copy_working_dir: true` to give each eval step a fresh copy instead:" and "`promptfoo eval` creates the workspace before each call and deletes it after that call's assertions have run. The Claude Agent SDK, OpenAI Codex SDK, and OpenCode SDK providers support it." and "Cloning requires Git 2.41 or newer. With older Git, `true` copies the directory and `'git'` returns an error."
- **Our assessment**: The workspace model is the mechanism that makes
  write-capable agent tests order-independent: without it, a test that edits a
  file poisons the fixture for every subsequent test in the same run, so pass/fail
  depends on test ordering (a flake source). The auto-mode value rule is worth
  extracting literally (Concrete Artifacts): `true` clones only when
  `working_dir` is a clean git repo root whose files all match the current
  commit, and copies otherwise — so "isolated" can silently mean "copied
  including `node_modules`" on a dirty tree. `'git'` is the strict variant and
  fails loudly when the precondition does not hold; that loudness is the reason
  to prefer it when the repo state is controllable.

### Claim 5: Workspace isolation has documented limits that bound the safety claim — responses are never cached (a cached response would lack the agent's changes), only eval steps get a workspace (a multi-turn red-team provider call *fails* instead of running in `working_dir`), submodules are unsupported — and, the crucial caveat, "it isn't a sandbox"
- **Evidence**: The "Workspaces have these limits" bullet list, especially the
  four bullets on caching, eval-step-only workspaces, the unsupported-link /
  Git-metadata rules, and the explicit isn't-a-sandbox sentence.
- **Confidence**: settled (documented product behavior and the vendor's own
  limit statement)
- **Quote**: "Responses are never cached, because a cached response would come without the agent's changes." and "Only eval steps get a workspace. When anything else calls the provider, such as a multi-turn red team strategy, the call fails instead of running in `working_dir` itself." and "A workspace keeps calls from affecting each other, but it isn't a sandbox. An agent with shell access can still reach the rest of the file system, so run untrusted agents in a container."
- **Our assessment**: The single most guide-relevant claim on the page, and
  the Ch06 boundary the Prospector flagged. `copy_working_dir` provides
  *test-to-test* isolation, not *host* isolation: each call gets a fresh
  directory, but a shell-capable agent can read/write outside it, so the
  workspace protects the eval fixtures, not the runner. Read together with the
  provider "read-only sandbox" postures (Claim 3), the accurate mental model is
  layered defaults, not one sandbox. Two further operational consequences:
  (a) caching is deliberately disabled for workspace calls, which means a
  write-capable eval run cannot be cheaply replayed from cache — the isolation
  and the cache are in tension; (b) workspace-only-on-eval-steps means
  multi-turn red-team strategies (which call the provider outside an eval step)
  fail rather than silently run against the real `working_dir`.

### Claim 6: Assertions can read the workspace through two response-metadata fields — `workingDir` (valid until the call's assertions run) and `workspaceDiff` (a unified diff for a clone, truncated beyond 100,000 characters) — and an `agent-rubric` grader runs in the same workspace so it can inspect the agent's changes
- **Evidence**: The assertion-metadata bullets and the `check-workspace.js`
  example, plus the `agent-rubric` sentence at the end of the section.
- **Confidence**: settled (documented product behavior)
- **Quote**: "`workingDir`: the workspace directory. It exists until the call's assertions have run." and "`workspaceDiff`: for a clone, the agent's changes as a unified diff against the cloned commit, including any commits the agent made. Diffs longer than 100,000 characters are truncated." and "An `agent-rubric` grader runs in the same workspace, so it can inspect the agent's changes."
- **Our assessment**: This is the file-level verification path that the
  final-text warning (Claim 9) says is necessary. Two reviewable limits: the
  diff is only produced for a *clone*, so `'copy'` mode leaves `workspaceDiff`
  undefined (the page's sample JS falls back to "The workspace is a copy, so
  there is no diff."), and the 100k-character truncation means a large or
  vendored-file diff is silently clipped — an assertion that greps the diff for
  a forbidden change can pass simply because the change landed beyond the
  truncation point. The `agent-rubric`-in-workspace note ties back to the
  model-graded note's agent-grader material.

### Claim 7: The path, not just the output, is assertable — `trajectory:step-count` can require that a `pytest*` command ran and that at least one reasoning step occurred, with `trajectory:tool-used` / `trajectory:tool-sequence` for exact tool paths — and the stated principle is "assert the path when the path matters"
- **Evidence**: The refactor example's `tracing: enabled` block + trajectory
  asserts, the following `trajectory:tool-used` pointer, and the "Evaluation
  principles" bullet of the same name.
- **Confidence**: settled (documented product behavior; the trace dependency
  is explicit on the page)
- **Quote**: "When you need to verify behavior rather than the agent's self-report, tracing is the better fit. It lets you assert that the agent actually ran tests, executed commands, or took multiple reasoning steps:" and "If your agent emits tool-oriented spans, add [`trajectory:tool-used`](/docs/configuration/expected-outputs/deterministic/#trajectorytool-used) or [`trajectory:tool-sequence`](/docs/configuration/expected-outputs/deterministic/#trajectorytool-sequence) to verify the exact tool path." and "**Assert the path when the path matters.** If the requirement is "ran tests," "asked for approval," or "used the MCP tool," do not rely only on the final answer. Use trace assertions or provider metadata."
- **Our assessment**: The methodology-level statement of the same assertion
  family the deterministic-metrics note catalogued at config level, and the
  reason to prefer it here: a refactor eval that only greps the final text for
  "pytest" and "passed" is grading the agent's *self-report*, which a
  plausible-but-untrue answer satisfies. The trajectory assertion is the
  control. The cost, which the page inherits and the sibling note documents, is
  that these assertions require trace data (Claim 12 of
  `docs-promptfoo-deterministic-metrics.md`): tracing must be enabled, the
  `otlp` endpoint configured, and the provider must emit tool-oriented spans, or
  the gate fails for infrastructure reasons.

### Claim 8: For app-server providers, the eval asserts on the runtime protocol, not the final message — the documented example checks `providerResponse.metadata.codexAppServer.serverRequests` for a deterministic command-approval request, explicitly *not* whether the reply "sounds reasonable"
- **Evidence**: The "App-server protocol and approval evals" section's
  motivating paragraph and its JavaScript assertion reading
  `context.providerResponse?.metadata?.codexAppServer?.serverRequests`.
- **Confidence**: settled (documented product behavior with a worked example)
- **Quote**: "Use Codex app-server when the behavior under test lives in the client protocol, not just the final text. Approval requests, item events, app connector events, plugin metadata, and thread lifecycle details are examples of app-server-specific surfaces." and "This eval is not asking whether the final message sounds reasonable. It checks whether the runtime requested command approval and whether promptfoo answered without a human in the loop. Keep these tests in disposable or read-only workspaces unless the expected side effect is part of the test."
- **Our assessment**: The cleanest corpus example of grading a *runtime
  permission event* instead of a natural-language claim. This matters for the
  guide because "did the agent ask before acting?" is a control property that
  cannot be read off the transcript — a model asked to "explain whether the
  command was allowed" can narrate a correct policy compliance while never
  triggering the protocol request. The assertion reads the protocol surface,
  which is the ground truth. The paired practitioner claim (deny writes,
  require human permission) already lives in the Prodcast note (Claim 3); this
  is the eval-side mechanism for testing it.

### Claim 9: An agent's output *is* its final text response, not the files it changed — so file-level verification must inspect the workspace or enable tracing, because the transcript describes what the agent says it did
- **Evidence**: The sentence introducing the refactoring example's limitation,
  plus the pointer to the isolated-workspace and tracing surfaces.
- **Confidence**: settled (documented product behavior)
- **Quote**: "The agent's output is its final text response describing what it did, not the file contents. For file-level verification, check the files in its [isolated workspace](#isolated-workspaces) or enable [tracing](/docs/tracing/)."
- **Our assessment**: A precise statement of why "grade the output" is
  insufficient for coding agents, and the seam between this page's methodology
  and the sibling assertion notes: the final text is a *claim about the change*,
  while the change itself lives in `workingDir`/`workspaceDiff` (Claim 6) or in
  trace spans (Claim 7). The guide should state this as a rule — an agent eval
  whose assertions only touch the final text cannot distinguish a correct
  self-report from a correct action.

### Claim 10: Regression gates for agent evals are cost/latency thresholds plus `--no-cache` and `--repeat 3` — the page gives a concrete cost band ($0.10–0.30 / 30–120 s for a security audit), requires `--no-cache` during development "so stale provider responses do not hide regressions," and treats a prompt that fails ~50% of the time as an *ambiguous prompt* to fix rather than a retry target
- **Evidence**: The "Cost and latency" and "Non-determinism" sections'
  threshold examples and their accompanying prose, plus the QA-checklist
  `--no-cache` and `--repeat 3` items.
- **Confidence**: settled for the mechanisms and the vendor's own `--no-cache`
  rationale; the `$0.10–0.30 / 30–120 s` band is a single illustrative figure,
  not a measured distribution
- **Quote**: "Agent tasks can be expensive. A security audit might cost $0.10–0.30 and take 30–120 seconds. Set thresholds to catch regressions:" and "`--no-cache` during development so stale provider responses do not hide regressions." and "The same prompt can produce different results across runs. Run evals multiple times with `--repeat 3` to measure variance. Write flexible assertions that accept equivalent phrasings:" and "If a prompt fails 50% of the time, the prompt is ambiguous. Fix the instructions rather than running more retries."
- **Our assessment**: The CI-gate checklist in methodology form. The
  `--no-cache` rationale is the caching note's thesis restated by the vendor for
  this surface (`docs-promptfoo-configuration-caching.md` Claim 8: a warm cache
  makes `--repeat` measure replayed outputs, not model variance), and the
  "50% failure = ambiguous prompt" rule is a genuinely useful triage heuristic
  for on-call: repeated flake in an agent eval usually indicts the instruction,
  not the model. The cost band is directional only (one audit task); do not
  port it as a universal threshold.

### Claim 11: Token distribution is a diagnostic for what the agent is actually doing — high prompt tokens with low completion tokens means the agent is reading files; the inverse means you are testing generation, not agency
- **Evidence**: The "Cost and latency" section's token-distribution paragraph
  and the "Evaluation principles" bullet of the same name.
- **Confidence**: emerging (a heuristic the vendor offers without a measured
  threshold)
- **Quote**: "Token distribution reveals what the agent is doing. High prompt tokens with low completion tokens means the agent is reading files. The inverse means you're testing the model's generation, not the agent's capabilities." and "**Check token patterns.** Huge prompt + small completion = agent reading files. Small prompt + large completion = you're testing the model, not the agent."
- **Our assessment**: A cheap, reusable operational diagnostic worth extracting
  even though it is heuristic: it is observable in the eval report without new
  instrumentation and it detects the same "you graded the model, not the agent"
  failure as a missing baseline. It pairs with Claim 2 (tier scoping) and the
  security-audit example's "~1M tokens" expectation. Treat the direction as
  reliable and any specific cut-off as unstated.

### Claim 12: Provider-enforced structured output is the recommended first eval shape — Codex `output_schema`, Codex app-server `output_schema`, Claude `output_format.json_schema`, and OpenCode `format` — validated downstream with `contains-json` (embedded JSON) vs `is-json` (provider returns only JSON)
- **Evidence**: The security-audit example (a bounded `output_schema` plus a
  JavaScript assertion counting seeded vulnerabilities) and the "Structured
  output" section's schema/assert guidance.
- **Confidence**: settled (documented product behavior)
- **Quote**: "Provider-enforced schemas (Codex `output_schema`, Codex app-server `output_schema`, Claude `output_format.json_schema`, and OpenCode `format`) make downstream assertions simpler. Use `contains-json` to validate output that might appear inside markdown code blocks, or `is-json` when the provider should return only JSON:" and "A plain LLM given the same prompt will explain how to do a security audit rather than actually doing one—it can't read the files. Expect high token usage (~1M) because Codex loads its system context regardless of codebase size."
- **Our assessment**: The `contains-json`/`is-json` distinction is the same
  spec decision the deterministic-metrics note records (its Claim 7), here
  framed for agent output; this page adds the *why structured-first* reasoning —
  a bounded schema turns a fuzzy agent task ("find the bugs") into a countable
  assertion ("did it find all 3 and flag at least one critical"). The "~1M
  tokens" note is the concrete illustration of agent-eval cost asymmetry: the
  provider's system context is loaded regardless of codebase size, so a
  tiny-repo eval is not proportionally cheaper.

### Claim 13: Safety defaults for coding-agent evals treat the agent as arbitrary code execution — never production credentials, real customer data, or internal-network access — with ephemeral no-network containers, read-only mounts, dummy keys, `disallowed_tools: ['Bash']`, Codex `sandbox_mode: read-only` with network/web-search disabled and a minimal `cli_env`, and read-only tool defaults for Claude Agent SDK / OpenCode SDK
- **Evidence**: The "Safety" section's opening warning, its sandboxing-option
  list, and the two provider-specific paragraphs (Codex, Claude/OpenCode).
- **Confidence**: settled (documented vendor guidance)
- **Quote**: "Coding agents execute arbitrary code. Never give them access to production credentials, real customer data, or network access to internal systems." and "For Codex SDK and Codex app-server evals, prefer `sandbox_mode: read-only` when the task only needs code inspection. Keep `network_access_enabled`, `web_search_mode`, and `web_search_enabled` disabled unless the test explicitly requires them. Pass only the environment variables Codex needs through `cli_env`; Codex providers use a minimal shell environment by default instead of inheriting the full parent process env." and "For Claude Agent SDK and OpenCode SDK evals, start with read-only file tools. Add write, edit, bash, MCP, or custom agent permissions only when the test asserts those behaviors directly."
- **Our assessment**: The Ch06-relevant posture, and it is more specific than a
  generic "sandbox your evals": least-privilege is expressed as concrete knobs
  (`disallowed_tools`, `sandbox_mode`, disabled network/search, minimal `cli_env`,
  read-only mounts with writes to separate volumes) plus the two hard
  prohibitions (no production creds, no customer data). Read against Claim 5's
  "it isn't a sandbox," the honest summary is: the *documents* recommend
  container-level isolation, while the workspace feature alone does not provide
  it — the safety is the operator's configuration, not a property of
  `copy_working_dir`.

### Claim 14: The release checklist frames coding-agent evals as integration tests — a plain-LLM baseline for file/tool tasks, at least one structured assertion, cost/latency thresholds, `--no-cache` during development, a disposable workspace for write-capable tests, trace/metadata assertions when the path matters, and `--repeat 3` for stability — validated locally with `validate config` before expensive runs
- **Evidence**: The "QA checklist" section's seven-item list and its local
  validation commands.
- **Confidence**: settled (documented vendor guidance)
- **Quote**: "Run coding agent evals like integration tests. A useful PR or release check includes:" and "For local provider work, validate configs before running expensive evals:" and "npm run local -- validate config -c examples/openai-codex-app-server/promptfooconfig.yml" and "npm run local -- eval -c examples/openai-codex-app-server/promptfooconfig.yaml --no-cache"
- **Our assessment**: The checklist is the synthesis of the page and the teeth
  of the Prospector's "CI-gateable" question: it converts the methodology claims
  into a reviewable list an operator can put on a PR template. Note the two
  items that map to this page's distinctive thesis — the mandatory baseline
  (Claim 2) and the trace/metadata assertion "when the intermediate path matters"
  (Claims 7-8) — because those are exactly the checks a text-output-only eval
  would omit.

## Concrete Artifacts

All artifacts copied from
https://www.promptfoo.dev/docs/guides/evaluate-coding-agents (sections named).
The page's code blocks arrive as collapsed single lines after HTML extraction;
line breaks were restored at YAML/JS boundaries only, with no wording changes.
Prose quotes elsewhere in this note are character-for-character from the
rendered page.

### Capability tiers (verbatim table from "Capability tiers")

| Tier | Example providers | Use when you need | Watch for |
| --- | --- | --- | --- |
| **0: Text** | `openai:gpt-6-sol`, `anthropic:claude-sonnet-5` | Code generation, explanation, JSON output, baseline behavior | No file reads, shell commands, or tool traces |
| **1: Coding agent SDK** | `openai:codex-sdk`, `anthropic:claude-agent-sdk`, `opencode:sdk` | Codebase reads, refactors, command runs, CI-friendly agent QA | Side effects, tool permissions, session state |
| **2: Rich client server** | `openai:codex-app-server`, `openinterpreter` | App-server events, approvals, skills, plugins, thread details | Experimental protocol and local child process |

### Provider selection and default safety posture (verbatim table from "Capability tiers")

| Provider | Best fit | Runtime boundary | Default safety posture |
| --- | --- | --- | --- |
| **OpenAI Codex SDK** | CI, automation, structured coding outputs, thread reuse | `@openai/codex-sdk` library | Git repo check, filesystem sandbox, network/search off unless enabled, minimal env |
| **OpenAI Codex app-server** | Rich-client protocol behavior, streamed items, approvals, skills, plugins, app connector events | Local `codex app-server` JSON-RPC process | Read-only sandbox, approvals declined, ephemeral threads, minimal env |
| **Claude Agent SDK** | Claude Code-compatible workflows, MCP-heavy tasks, local skills | `@anthropic-ai/claude-agent-sdk` library | No tools by default; configured working dirs are read-only until write tools opt in |
| **OpenCode SDK** | Provider-agnostic coding agent comparisons | OpenCode SDK with a promptfoo-started or existing server | Temporary workspace by default; working dirs start with read-only tools |
| **Open Interpreter** | Multi-backend coding agent and harness comparisons | Local `interpreter app-server` JSON-RPC process | Read-only sandbox, approvals declined, ephemeral threads, minimal env |

### Security audit with structured output (verbatim from the section of that name)

```yaml
description: Security audit
prompts:
  - Analyze all Python files for security vulnerabilities.
providers:
  - id: openai:codex-sdk
    config:
      model: gpt-6-sol
      working_dir: ./test-codebase
      output_schema:
        type: object
        required: [vulnerabilities, risk_score, summary]
        additionalProperties: false
        properties:
          vulnerabilities:
            type: array
            items:
              type: object
              required: [file, severity, issue, recommendation]
              properties:
                file: { type: string }
                severity: { type: string, enum: [critical, high, medium, low] }
                issue: { type: string }
                recommendation: { type: string }
          risk_score: { type: integer, minimum: 0, maximum: 100 }
          summary: { type: string }
tests:
  - assert:
      - type: contains-json
      - type: javascript
        value: |
          const result = typeof output === 'string' ? JSON.parse(output) : output;
          const vulns = result.vulnerabilities || [];
          const hasCritical = vulns.some(v => v.severity === 'critical' || v.severity === 'high');
          return {
            pass: vulns.length >= 2 && hasCritical,
            score: Math.min(vulns.length / 5, 1.0),
            reason: `Found ${vulns.length} vulnerabilities`
          };
```

### App-server approval eval (verbatim from "App-server protocol and approval evals")

```yaml
description: Codex app-server command approval eval
prompts:
  - |
    Try to run `touch approval-check.txt` with a shell command.
    If the sandbox blocks it, request the permission needed to rerun it.
    Explain whether the command was allowed.
providers:
  - id: openai:codex-app-server:gpt-6-sol
    config:
      sandbox_mode: read-only
      approval_policy: on-request
      approvals_reviewer: user
      server_request_policy:
        command_execution: decline
        file_change: decline
        mcp_elicitation: decline
tests:
  - assert:
      - type: javascript
        value: |
          const requests = context.providerResponse?.metadata?.codexAppServer?.serverRequests ?? [];
          const commandRequest = requests.find((request) =>
            String(request.method).includes('commandExecution') ||
            String(request.method).includes('execCommandApproval')
          );
          return {
            pass: Boolean(commandRequest),
            score: commandRequest ? 1 : 0,
            reason: commandRequest
              ? 'Observed a deterministic command approval request.'
              : 'No command approval request was observed.'
          };
```

### Refactor with test verification + trajectory asserts (verbatim from the sections of those names)

```yaml
description: Refactor with test verification
prompts:
  - |
    Refactor user_service.py to use bcrypt instead of MD5.
    Run pytest and report whether tests pass.
providers:
  - id: anthropic:claude-agent-sdk
    config:
      model: claude-sonnet-5
      working_dir: ./user-service
      copy_working_dir: true
      append_allowed_tools: ['Write', 'Edit', 'MultiEdit', 'Bash']
      permission_mode: acceptEdits
tests:
  - assert:
      - type: javascript
        value: |
          const text = String(output).toLowerCase();
          const hasBcrypt = text.includes('bcrypt');
          const ranTests = text.includes('pytest') || text.includes('test');
          const passed = text.includes('passed') || text.includes('success');
          return {
            pass: hasBcrypt && ranTests && passed,
            reason: `Bcrypt: ${hasBcrypt}, Tests: ${ranTests && passed}`
          };
      - type: cost
        threshold: 0.50
```

Trajectory variant (with tracing enabled):

```yaml
tracing:
  enabled: true
  otlp:
    http:
      enabled: true
providers:
  - id: openai:codex-sdk
    config:
      working_dir: ./repo
      enable_streaming: true
tests:
  - assert:
      - type: trajectory:step-count
        value:
          type: command
          pattern: 'pytest*'
          min: 1
      - type: trajectory:step-count
        value:
          type: reasoning
          min: 1
```

### Workspace-diff assertion (verbatim from "Isolated workspaces")

`check-workspace.js`:

```javascript
const fs = require('fs');
const path = require('path');

module.exports = (output, context) => {
  const { workingDir, workspaceDiff } = context.providerResponse.metadata;
  const source = fs.readFileSync(path.join(workingDir, 'user_service.py'), 'utf8');
  const pass = source.includes('bcrypt') && !source.includes('md5');
  return {
    pass,
    score: pass ? 1 : 0,
    reason: workspaceDiff ?? 'The workspace is a copy, so there is no diff.',
  };
};
```

### QA/release checklist and local validation (verbatim from "QA checklist")

```
- A plain LLM baseline for tasks that require file or tool access.
- At least one structured assertion (`is-json`, `contains-json`, JavaScript, or `llm-rubric`).
- Cost and latency thresholds for long-running tasks.
- `--no-cache` during development so stale provider responses do not hide regressions.
- A disposable workspace for write-capable tests.
- Trace or metadata assertions when the intermediate path matters.
- A repeated run (`--repeat 3`) for prompts that are expected to be stable.
```

```
npm run local -- validate config -c examples/openai-codex-app-server/promptfooconfig.yml
npm run local -- eval -c examples/openai-codex-app-server/promptfooconfig.yaml --no-cache
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 12**
    ("Trajectory assertions require trace data. Enable tracing for the eval and
    use a provider that emits tool-oriented spans or attributes.") — the
    config-level statement of the dependency this page's trajectory asserts
    (Claim 7) rely on: both notes agree the trace/trajectory family is only as
    live as the tracing pipeline. (Verified: #1289 Claim 12, read in full.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` **Claim 6** (cost
    requires provider-reported cost plus `--no-cache`) and **Claim 14**
    (`latency` requires `--no-cache`) — the mechanism behind this page's
    cost/latency thresholds and its `--no-cache`-during-development rule
    (Claim 10). (Verified: #1289 Claims 6, 14.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` **Claim 11** (the
    trace/trajectory assertion family the hub page catalogues — `trace-span-count`,
    `trace-error-spans`, `skill-used`, `trajectory:*`, `guardrails`) and
    **Claim 10** (the deterministic-vs-model-assisted split) — this page selects
    from that catalogue for the agent-eval methodology but does not re-derive it.
    (Verified: #1287 Claims 10, 11.)
  - `source-notes/docs-promptfoo-model-graded-metrics.md` **Claim 11**
    (`agent-rubric` default `openai:codex-sdk`, isolated/read-only/no-approvals,
    supported providers include Claude Agent SDK and OpenCode SDK) — matches this
    page's "an `agent-rubric` grader runs in the same workspace" (Claim 6) and
    the provider tiers (Claim 2), i.e. the same agent runtimes serve as both
    eval target and grader. (Verified: #1305 Claim 11.)
  - `source-notes/docs-promptfoo-configuration-caching.md` **Claim 8**
    (`--no-cache` + `--repeat` is required for every run to make fresh LLM
    calls; per-repeat cache namespaces) — the mechanism behind this page's
    `--no-cache` rationale and `--repeat 3` guidance (Claim 10). Note the
    complement: this page's workspace calls opt *out* of caching entirely
    (Claim 5), the write-capable case where the cache would be wrong by
    construction. (Verified: #1275 Claim 8.)
  - `source-notes/blog-promptfoo-owasp-red-teaming.md` **Claim 4** (pre-deployment
    red teaming integrated into CI/CD and run on a recurring schedule) — the
    recurring-CI-gate discipline this page's QA checklist (Claim 14)
    operationalizes for coding agents. (Verified: #555 Claim 4.)
  - `source-notes/blog-promptfoo-model-upgrades-break-agent-safety.md` **Claim 1**
    (a GPT-4o→GPT-4.1 upgrade dropped injection resistance 94%→71%) — the
    existence proof for why the regression thresholds and re-run discipline
    (Claim 10) matter: an agent eval gate exists to catch exactly this kind of
    silent capability change. (Verified: #482 Claim 1.)

- **Contradicts**: None identified, and no contradiction issue filed. This is
  first-party vendor documentation of one guide page and opposes no existing
  source-note claim. Checked `CONTRADICTIONS.md` (no `C-NNN` entries; the file
  is empty of open contradictions) and open `contradiction`-labeled issues —
  19 open, none about coding-agent eval, provider tiers, workspace isolation, or
  the trajectory assertions on this page. The nearest surface, open **#1307**
  (promptfoo missing-trace semantics: built-in trace-* assertions throw vs
  custom-JS trace gate passes green when tracing is off), is a *sibling*
  distinction, not a conflict with anything here: this page's trajectory asserts
  are in the throw-on-missing-trace family (corroborated by #1289 Claim 12), so
  it sits on the throw side of #1307 rather than opposing it.

- **Extends**:
  - `source-notes/docs-google-sre-prodcast-04-09-ai-agents.md` **Claim 7**
    (evaluation is the golden question and production is harder to evaluate than
    coding agents because "production is not a sandbox") and **Claim 10**
    (postmortems are training data because they carry the full *trajectory*, not
    just the final mitigation) — the practitioner counterpart to this page's two
    theses: that workspaces isolate but "isn't a sandbox" (Claim 5) and that an
    eval should assert the *path* (Claim 7). Where the Prodcast episode argues
    trajectory-matching is the gold standard for production agents, this page
    supplies the concrete eval-harness mechanics (trajectory asserts,
    `workspaceDiff`, the container caveat) for doing so on coding agents.
    (Verified: #105 Claims 7, 10.)
  - `source-notes/docs-promptfoo-deterministic-metrics.md` (#1289) — extends the
    trace/trajectory family from a config reference into the coding-agent
    methodology layer: the provider tiers, the workspace model, and the
    LLM-baseline rule are what turn the assertions the #1289 note catalogues into
    an agent-eval gate. (Verified: #1289 Claims 6, 12, 14 re-read.)
  - `source-notes/docs-promptfoo-assertions-metrics.md` (#1287) — extends the hub
    page's assertion-family overview to the agent-system case; this page answers
    *which* assertions to reach for when the system under test can read files,
    run commands, and request approvals. (Verified: #1287 Claims 10, 11.)

- **Novel**: First corpus coverage of **coding-agent eval methodology as a
  system-eval discipline**:
  1. **The agent-vs-function thesis with its three compounding reasons**
     (Claim 1) — the scoping argument, not another assertion type.
  2. **The three capability tiers and the same-model-different-harness point**
     (Claim 2), plus the **per-provider default safety-posture table and the
     `codex-desktop` alias caveat** (Claim 3).
  3. **The `copy_working_dir` workspace model** — value semantics, Git 2.41
     precondition, and the eval-step-only/fail-loud behavior (Claims 4-5).
  4. **The explicit "it isn't a sandbox" boundary** (Claim 5) — the Ch06-relevant
     limit that bounds what workspace isolation buys.
  5. **Workspace-inspection metadata** (`workingDir`, `workspaceDiff` with its
     100k-char truncation) and the `agent-rubric`-in-workspace note (Claim 6).
  6. **App-server approval evals graded on `serverRequests`** rather than the
     final message (Claim 8) — the runtime-permission-event assertion.
  7. **The agent-eval regression-gate checklist** — cost/latency thresholds,
     `--no-cache`, `--repeat 3`, and the "50% failure = ambiguous prompt" rule
     (Claims 10, 14), plus the **token-pattern diagnostic** (Claim 11).

## Guide Impact

- **Chapter 03 (Runbooks and Agents) — "Agent evaluation in production"
  (`guide/03-runbooks-and-agents.md:268`)**: Add a coding-agent eval subsection
  beside "Golden labels from historical incidents." The Prodcast-derived rule
  already says "evaluate the agent's trajectory before it acts"; this source
  supplies the harness mechanics for coding agents specifically:
  - Scope the eval by capability tier and always include a plain-LLM baseline
    for file/tool tasks (Claims 1-2); a baseline that fails the file task is the
    control that proves the agent harness is doing work
    [source: docs-promptfoo-evaluate-coding-agents, Claims 1, 2] [emerging].
  - Assert the path, not just the final text: `trajectory:step-count` /
    `trajectory:tool-used` / `trajectory:tool-sequence` for "ran tests" / "used
    the tool" requirements, and app-server `serverRequests` for "asked for
    approval" (Claims 7-8), because the agent's output is its self-report, not
    the change (Claim 9) [source: docs-promptfoo-evaluate-coding-agents, Claims
    7, 8, 9] [emerging].
  - Adopt the QA/release checklist as the PR-gate template (Claim 14): baseline,
    ≥1 structured assertion, cost/latency thresholds, `--no-cache` during
    development, a disposable workspace for write-capable tests, trace/metadata
    assertions when the path matters, `--repeat 3` for stable prompts.
- **Chapter 03 — read/write capability boundary and sandboxing
  (`guide/03-runbooks-and-agents.md:140` and the automation-safety baseline at
  :78)**: Record the evaluated-workspace limit explicitly: `copy_working_dir`
  gives each eval step a fresh directory but "isn't a sandbox," so a
  shell-capable agent can still reach the host filesystem and untrusted agents
  belong in a container (Claim 5). Pair it with the safety defaults — no
  production credentials/customer data/internal-network access, read-only
  mounts, dummy keys, `disallowed_tools: ['Bash']`, disabled network/search
  (Claim 13) — as the eval-time expression of the chapter's read/write rule.
  This connects to the Prodcast note's "production is not a sandbox" (its
  Claim 7) via the new Cross-Reference.
- **Chapter 05 (LLM Ops Reliability) — evaluation and measurement methodology
  (`guide/05-llm-ops-reliability.md:386`) and "A gate that cannot fail is not a
  gate" (`:655`)**: Extend the gate checklist with the agent-eval regression
  items — cost/latency thresholds, `--no-cache` (cached responses are stale
  evidence, corroborating `docs-promptfoo-configuration-caching.md` Claim 8),
  and `--repeat 3` for non-determinism (Claim 10). Add the triage heuristic:
  "if a prompt fails 50% of the time, the prompt is ambiguous" — fix the
  instruction rather than adding retries. The `workspaceDiff` 100k-char
  truncation (Claim 6) is a new "a green assertion may verify nothing" case: a
  diff-grep assertion can pass because the change fell outside the clipped diff.
- **Chapter 06 (Security and Trust) — "Red-teaming as a CI gate"
  (`guide/06-security-and-trust.md:120`)**: Use the app-server approval eval
  (Claim 8) as the canonical "test that the agent asked permission" pattern —
  it grades the runtime protocol event rather than the reply text — and the
  workspace-isn't-a-sandbox caveat (Claim 5) as the reason a write-capable eval
  gate must run inside a container, not merely with `copy_working_dir`.

## Extraction Notes

- Source read in full via direct fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/guides/evaluate-coding-agents). It is a single
  self-contained guide page. **Sub-pages followed: none** — the outbound links
  are the per-provider reference pages
  (`openai-codex-sdk`, `openai-codex-app-server`, `claude-agent-sdk`,
  `opencode-sdk`, `openinterpreter`), the tracing docs, the
  deterministic-assertions anchor for `trajectory:tool-used`/`:tool-sequence`,
  and `red-team/coding-agents` / `sandboxed-code-evals` guides. Each is either a
  provider-config reference (no new methodology) or already-mined assertion
  material (`docs-promptfoo-deterministic-metrics.md` owns the trajectory
  catalogue), so none was re-fetched per MINER.md §1; the page reproduces the
  configs it needs inline.
- **Scope discipline (per the Prospector's "extract the delta, not the page")**:
  deliberately not re-derived here are the generic assertion primitives already
  owned by the sibling notes — the full `trajectory:*` catalogue
  (`docs-promptfoo-deterministic-metrics.md`), the `llm-rubric` /
  `agent-rubric` grader semantics (`docs-promptfoo-model-graded-metrics.md`),
  and the hub aggregation/scoring model (`docs-promptfoo-assertions-metrics.md`).
  This note extracts the *agent-system eval methodology* — tiers, workspace
  isolation, path assertions, regression thresholds, safety, checklist — and
  cites the primitives by claim rather than restating them.
- Quotes were verified character-for-character against the fetched rendered
  page. Code blocks arrive as collapsed single lines after HTML extraction; line
  breaks were restored at YAML/JS boundaries only (no wording changes), the same
  convention as the sibling promptfoo config notes. The capability-tier and
  provider tables were copied row-for-row.
- **Cross-ref verification (§4b)**: every cited claim number was located in the
  cited note and its content checked against what it is cited for — #1289
  Claims 6/12/14, #1287 Claims 10/11, #1305 Claim 11, #1275 Claim 8, #555
  Claim 4, #482 Claim 1, #105 Claims 7/10. No claim numbers invented; no quotes
  attributed to other notes.
- **Contradiction scan**: none filed. `CONTRADICTIONS.md` has no `C-NNN`
  entries; `gh issue list --label contradiction --state open` returns 19 issues,
  none touching coding-agent eval, provider tiers, workspace isolation, or
  trajectory assertions. The nearest, **#1307** (missing-trace semantics), is a
  sibling distinction this page sits on the throw side of, not a conflict.
- **Candidate dismissal** (from `miner-related-notes.md`, read before writing
  Cross-References; candidates are suggestions only — cited or dismissed by
  name):
  - `docs-google-sre-prodcast-04-09-ai-agents.md` — **cited** (Extends,
    Claims 7, 10) as the practitioner counterpart to the sandbox/trajectory
    theses.
  - `blog-promptfoo-owasp-red-teaming.md` — **cited** (Corroborates, Claim 4)
    for the recurring-CI-gate theme.
  - `docs-promptfoo-enterprise-findings-reports.md` — Enterprise findings/
    report/export surface; no eval-harness methodology; dismissed.
  - `docs-promptfoo-enterprise-guardrails.md` — Enterprise runtime guardrail
    enforcement (HTTP gate contract); different layer (runtime control vs
    eval-time grading); dismissed.
  - `docs-langfuse-mcp-server.md` — Langfuse docs MCP server; unrelated vendor;
    dismissed.
  - `blog-incidentio-ai-sre-incident-run.md` — incident.io AI-SRE incident
    walkthrough; no coding-agent eval surface; dismissed.
  - `docs-litellm-batches-api.md` — LiteLLM batch rate-limit accounting; no
    eval/agent surface; dismissed.
  - `blog-pagerduty-sre-agent-triage.md` — PagerDuty SRE-agent incident triage;
    agent *operations*, not agent *eval*; dismissed.
  - `docs-google-sre-reliable-product-launches.md` — Google launch-process
    discipline; no LLM-eval content; dismissed.
  - `docs-google-sre-team-lifecycles.md` — SRE team org/lifecycles; no
    LLM-eval content; dismissed.
  - The additional cited cross-refs (`docs-promptfoo-deterministic-metrics.md`,
    `docs-promptfoo-assertions-metrics.md`, `docs-promptfoo-model-graded-metrics.md`,
    `docs-promptfoo-configuration-caching.md`,
    `blog-promptfoo-model-upgrades-break-agent-safety.md`) were found by
    searching `source-notes/` (`copy_working_dir`, `trajectory:tool-used`,
    `agent-rubric`, `codex-sdk`, etc.), per the Prospector's overlap list and
    MINER.md §4.
- `confidence_overall` is `emerging`, matching the sibling promptfoo notes: the
  mechanism/default claims (provider tiers, workspace semantics, trajectory
  asserts, safety defaults) are settled-for-product-behavior and directly
  checkable against an installed CLI, but this is vendor documentation with no
  measured gate-failure/flake rate, one illustrative cost band, and no
  independent practitioner validation; the operational framing (the
  "isn't-a-sandbox" scope of the safety claim, the diff-truncation gap, the
  ambiguous-prompt heuristic) is the Miner's synthesis on top of documented
  behavior.
- `registry/sources.json` and `registry/claims-index.json` were NOT edited; they
  are derived indexes rebuilt by `scripts/build_registry.py` /
  `scripts/build_claims_index.py` after merge.
