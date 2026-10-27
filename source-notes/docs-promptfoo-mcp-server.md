---
source_url: https://www.promptfoo.dev/docs/integrations/mcp-server
source_type: docs
title: "Promptfoo MCP Server: Eval and Red-Team Tooling Exposed to Agents — the Twelve-Tool Catalog, the STDIO/HTTP Trust Split, and the Documented Absence of Auth"
author: "Promptfoo (vendor documentation; page footer last updated 2026-10-26 by renovate[bot])"
date_published: 2026-10-26
date_extracted: 2026-10-27
last_checked: 2026-10-27
status: current
confidence_overall: emerging
issue: "#1891"
---

# Promptfoo MCP Server: Eval and Red-Team Tooling Exposed to Agents

> Promptfoo's own docs page for exposing its eval/red-team test CLI to
> MCP-capable agents: a twelve-tool surface (validate config, test provider,
> run evals, generate datasets, run and generate red-team scans, publish
> shareable results), launched over STDIO or an HTTP port at `/mcp` with a
> `/health` endpoint, inheriting every provider credential from the
> environment — and documenting no authentication, authorization, or approval
> gate anywhere on the page.

## Source Context

- **Type**: docs (vendor integration page — promptfoo
  `/docs/integrations/mcp-server`; page footer "Last updated on **Oct 26,
  2026** by **renovate\[bot\]**")
- **Author credibility**: Promptfoo, the commercial LLM eval/red-team vendor,
  documenting its own shipped `promptfoo mcp` subcommand and the per-client
  configs that launch it. Tool names, transport flags, env-var behavior, error
  strings, and the CLI invocation are checkable against an installed CLI, so
  the mechanics claims are authoritative. The page reports **no** run metrics,
  no latency/cost figures, no auth testing, and no evidence that agents use the
  tools well — every efficacy-adjacent statement is vendor assertion.
- **Scope**: The execution-side control surface: how to start the MCP server,
  how to register it with Cursor/Claude Desktop, the twelve exposed tools and
  their one-line descriptions, four example agent workflows, the STDIO-vs-HTTP
  transport choice, best-practice ordering, troubleshooting, the HTTP
  `/mcp` + `/health` shapes, and environment-variable inheritance. It does NOT
  document tool input schemas, auth, rate limits, tenancy, approval gates,
  audit logging, or concurrency limits beyond the `run_evaluation` argument
  description. It also does not cover the separate enterprise **MCP Proxy**
  product (`/mcp/`, rejected as marketing in closed #1147) or the
  authoring-side Agent Skills bundle (`docs-promptfoo-agent-skill.md`).
- **Sub-pages followed** (per MINER.md §1): none. The page is self-contained;
  its outbound links are the MCP protocol home page, the promptfoo docs home,
  and an examples directory — none adds substantive detail about this server's
  contract. Sibling pages already have their own notes (cited below), so they
  were not re-read as sub-pages.

## Extracted Claims

### Claim 1: Promptfoo ships its eval tooling as an MCP server whose stated purpose is exposing "eval tools to AI agents," with two transports — STDIO for desktop clients and HTTP for web/remote integrations
- **Evidence**: The page subtitle, the two-command Quick Start, and the
  Transport Types section's per-transport rationale.
- **Confidence**: settled (shipped CLI surface; transport flags are checkable)
- **Quote**: "Expose promptfoo's eval tools to AI agents via Model Context
  Protocol (MCP)." and "**STDIO (`--transport stdio`)**: For desktop AI tools
  (Cursor, Claude Desktop) that communicate via stdin/stdout" and
  "**HTTP (`--transport http`)**: For web applications, APIs, and remote
  integrations that need HTTP endpoints"
- **Our assessment**: This is the load-bearing inversion for the guide: promptfoo
  normally *evaluates* agents, but this page makes the eval harness itself the
  agent's tool provider. The transport split is the whole deployment decision —
  STDIO keeps the server a child process of the developer's editor, while HTTP
  turns it into a service. The page treats that as a convenience (desktop vs
  web) rather than as a trust-boundary change; we treat it as the latter.

### Claim 2: The exposed surface is twelve tools in four groups — four core eval tools, three generation/comparison tools, two red-team tools, and three config/test tools — including `run_assertion`, which the Prospector's triage list omitted
- **Evidence**: The "Available Tools" section's four sub-lists and their
  one-line descriptions.
- **Confidence**: settled (verbatim tool inventory)
- **Quote**: "**`list_evaluations`** - Browse your evaluation runs with optional
  dataset filtering" and "**`run_evaluation`** - Execute evaluations with
  custom parameters, test case filtering, and concurrency control" and
  "**`share_evaluation`** - Generate publicly shareable URLs for evaluation
  results" and "**`run_assertion`** - Test individual assertion rules against
  outputs for debugging"
- **Our assessment**: Buy the inventory as the exact contract. The delta versus
  the Prospector's list is `run_assertion` — a debugging tool that executes an
  assertion (and can therefore make a model-graded call) against provided
  output. That matters because it is another execution path, not a read. The
  full catalog is captured verbatim under Concrete Artifacts.

### Claim 3: The page never labels tools read-only vs mutating; the split must be inferred from the verb and description — and at least seven tools execute work that can spend provider tokens or change run state, while `share_evaluation` publishes externally
- **Evidence**: No "read-only", "write", "mutating", or permission column
  appears anywhere in "Available Tools"; the descriptions distinguish
  "Browse"/"Get" from "Execute"/"Generate"/"Compare"/"share". The example
  workflows confirm `run_evaluation`, `compare_providers`, and `redteam_run`
  actually launch work.
- **Confidence**: emerging (the catalogue is settled; the read/write
  classification is our inference, not vendor-documented)
- **Quote**: "**`generate_dataset`** - Generate test datasets using AI for
  comprehensive evaluation coverage" and "**`compare_providers`** - Compare
  multiple AI providers side-by-side for performance and quality" and
  "**`redteam_run`** - Execute comprehensive security testing against AI
  applications with dynamic attack probes"
- **Our assessment**: This is the highest-value gap on the page. For Ch03's
  default-deny-writes rule, an operator needs a read/write split, and the
  vendor supplies none. Our inference: **pure reads/validation** —
  `list_evaluations`, `get_evaluation_details`, `validate_promptfoo_config`;
  **cost-incurring execution** — `run_evaluation`, `compare_providers`,
  `test_provider`, `generate_dataset`, `generate_test_cases`, `redteam_run`,
  `redteam_generate`, `run_assertion` (model-graded assertions call a judge);
  **externally visible publication** — `share_evaluation`. `test_provider`
  is easy to misread as a read, but it makes a provider call and spends
  tokens. Treat this split as a review checklist, not as vendor contract.

### Claim 4: `share_evaluation` publishes eval results to publicly shareable URLs, and the page documents no review or approval step before an agent can invoke it
- **Evidence**: The tool's own description; the "Basic Evaluation Workflow"
  and other examples never gate `share_evaluation`; there is no approval,
  confirmation, or scope discussion anywhere on the page.
- **Confidence**: settled for the capability (documented tool description);
  emerging for the absence of a gate (argument from silence — the page could
  simply omit it)
- **Quote**: "**`share_evaluation`** - Generate publicly shareable URLs for
  evaluation results"
- **Our assessment**: This is the clearest externally visible side effect in
  the catalog: an agent-invoked call can take internal eval output (prompts,
  test cases, model responses, failure evidence) and publish it outside the
  trust boundary. The page's only red-team safety advice is about scanning,
  not sharing. We flag this as a Ch06 gate requirement, not as a vulnerability
  claim — the page may rely on an unstated promptfoo default. Note the corpus
  already documents `promptfoo share` as a read-only programmatic surface
  (`docs-promptfoo-enterprise-findings-reports.md` Claim 10); this tool makes
  the same publication step agent-callable.

### Claim 5: HTTP mode serves a JSON-RPC `/mcp` endpoint and a `/health` endpoint, and the page documents no authentication, host binding, TLS, or access-control mechanism for either
- **Evidence**: The "Custom HTTP Integrations" Node.js `fetch` against
  `http://localhost:3100/mcp`, the troubleshooting instruction to verify
  `curl http://localhost:3100/health`, and the complete absence of an auth,
  token, header, or reverse-proxy section.
- **Confidence**: settled for the endpoint shapes; emerging for the "no auth"
  reading (again an argument from silence — the docs never state that auth is
  absent, they simply never mention it)
- **Quote**: "For HTTP transport, you can integrate with any system that
  supports HTTP:" and "For HTTP transport, verify with `curl
  http://localhost:3100/health`"
- **Our assessment**: The docs only ever show `localhost`, so we should not
  assert that the server binds a public interface. What we can say is that the
  documented deployment gives an operator no authentication story at all: if
  they expose the port (container, reverse proxy, shared host), the JSON-RPC
  surface accepts `tools/call` requests that execute evals and red-team runs
  with the process's provider credentials. Ch06 should treat "MCP server over
  HTTP" as requiring an auth layer the vendor docs do not supply, exactly as
  it treats Langfuse's authenticated data plane as the safe pattern.

### Claim 6: The server "respects all promptfoo environment variables," so provider API keys and config-directory settings are in scope of every agent-initiated tool call
- **Evidence**: The Environment Variables section names `OPENAI_API_KEY`,
  `ANTHROPIC_API_KEY`, and `PROMPTFOO_CONFIG_DIR` and then starts the server
  with that environment.
- **Confidence**: settled (documented inheritance behavior)
- **Quote**: "The MCP server respects all promptfoo environment variables:" and
  "export OPENAI_API_KEY=sk-..." and "export ANTHROPIC_API_KEY=sk-ant-..."
- **Our assessment**: Buy it, and read it as a credential-scope statement: any
  client that can call the server can cause provider calls billed to those
  keys. Combined with Claim 5, the HTTP transport is a credential-bearing
  execution service with no documented access control. For Ch03/Ch06 the
  actionable rule is to give the MCP server a dedicated, least-privilege key
  set rather than the operator's ambient shell environment.

### Claim 7: `npx promptfoo@latest` is the documented default for both server launch and the checked-in client configs, making a floating version part of the agent's control path
- **Evidence**: The Quick Start commands, both Cursor and Claude Desktop
  `mcpServers` blocks (args `["promptfoo@latest", "mcp", "--transport",
  "stdio"]`), and the explicit callout that regular usage should "Always use
  `npx promptfoo@latest`".
- **Confidence**: settled (verbatim invocation and config)
- **Quote**: "**For regular usage:** Always use `npx promptfoo@latest` as shown
  above."
- **Our assessment**: This directly contradicts the corpus's pin-everything
  rule for security tooling (`docs-promptfoo-code-scan-github-action.md` Claim
  3 documents the same vendor's *other* artifact moving away from runtime
  `promptfoo@latest` resolution after v0.1.8). The MCP page's own slim-install
  exception (Claim 8) shows the authors know same-project resolution matters.
  For the guide: a config file that launches `@latest` re-resolves the entire
  eval/red-team toolchain on every agent session — pin the version in the
  `args` array and verify provenance, as with any other agent-invoked binary.

### Claim 8: Slim installs omit the optional `@modelcontextprotocol/sdk`, so the server fails with a required-SDK error — the fix installs both packages locally and then runs `npx promptfoo ...` rather than `npx promptfoo@latest ...`
- **Evidence**: The prerequisites callout, the initial Prerequisites bullet,
  the troubleshooting error text, and the explicit instruction about which
  invocation resolves both packages.
- **Confidence**: settled (documented failure symptom and remedy)
- **Quote**: "If the error says `@modelcontextprotocol/sdk` is required,
  install that optional runtime package alongside the promptfoo installation
  that runs the server." and "When using that local slim-install setup, run the
  MCP commands below as `npx promptfoo ...` instead of `npx promptfoo@latest
  ...` so both packages resolve from the same project."
- **Our assessment**: A concrete operational gotcha with a side effect the page
  does not spell out: the remedy silently changes the version-resolution
  posture from floating-latest (Claim 7) to same-project local resolution. That
  is the *safer* mode, but it is documented only as a troubleshooting step for
  slim installs, not as the recommended production config. Worth calling out
  in a runbook: "SDK required" is an install-shape problem, not an MCP
  configuration error.

### Claim 9: Eval discovery is working-directory (or config-directory) scoped — "Eval not found" means the agent is in the wrong directory, and config errors mean the local `promptfooconfig.yaml` is missing or invalid
- **Evidence**: The Tool-Specific Errors block: "Eval not found" → use
  `list_evaluations`, ensure the cwd has promptfoo evaluation data; "Config
  error" → validate and verify `promptfooconfig.yaml`.
- **Confidence**: settled (documented troubleshooting behavior)
- **Quote**: "Ensure you're in a directory with promptfoo evaluation data" and
  "Verify `promptfooconfig.yaml` exists and is valid"
- **Our assessment**: This is the most under-appreciated operational constraint
  on the page. The "eval catalog" is not a shared service registry; it is
  whatever the server process can see from its working directory (plus
  `PROMPTFOO_CONFIG_DIR`). An MCP client launched from a different project root
  sees a different set of evals, and an agent asked to "check the last eval"
  can silently be reading the wrong store. For Ch03's agent runbooks, pin the
  server's cwd explicitly and treat a wrong-directory start as a confounder
  before trusting any "no evals found" conclusion.

### Claim 10: The page's safe ordering is validate config → test provider → small subset → full run, with a parallel red-team sequence of basic plugins → review generated cases → run → analyze
- **Evidence**: "Best Practices" sections 1-4 ("Start Small", "Use Filtering",
  "Iterative Testing", "Security First") and the four example workflows, each
  of which spells out the same sequence.
- **Confidence**: emerging (a documented discipline; no evidence it is enforced
  or measured)
- **Quote**: "Validate configuration first" and "Test providers individually
  before comparisons" and "Run small evaluation subsets before full runs" and
  "Start with basic plugins before advanced attacks" and "Review generated test
  cases before running"
- **Our assessment**: Buy the ordering — it is the same "validate → cheap probe
  → bounded run → full run" sequence the guide already uses for pre-deploy
  gates. But note the page states it as advice to whoever is driving the
  agent, and nothing in the tool contract enforces it: `run_evaluation` and
  `redteam_run` are callable directly, with no required prior validation, no
  size cap beyond the caller-supplied filter, and no approval step. The
  sequence is a good default prompt, not a gate. In particular, "review
  generated test cases before running" is the only approval-like instruction,
  and it is a human-in-the-loop suggestion the agent can skip.

### Claim 11: The HTTP surface is callable by any JSON-RPC-capable script, not just an MCP client — the page's own example is a raw `fetch` POST with `method: "tools/call"`
- **Evidence**: The "Custom HTTP Integrations" code block posts to
  `http://localhost:3100/mcp` with `{ method: 'tools/call', params: { name:
  'list_evaluations', arguments: { datasetId: 'my-dataset' } } }`.
- **Confidence**: settled (verbatim example)
- **Quote**: "For HTTP transport, you can integrate with any system that
  supports HTTP:"
- **Our assessment**: Worth recording because it widens the threat model:
  "MCP" here is a JSON-RPC convention, not a transport-level client check. A
  shell script, CI job, or non-MCP agent can drive the same tools if it can
  reach the port. That makes the missing auth (Claim 5) more consequential —
  the boundary is the network/OS process boundary, not the MCP client
  identity.

### Claim 12: Registering the server with Cursor or Claude Desktop means writing a config whose `command`/`args` the client executes — `.cursor/mcp.json` or the platform-specific Claude Desktop config — followed by a full restart
- **Evidence**: The per-client config artifacts, the three Claude Desktop
  config paths (macOS/Windows/Linux), and the restart instruction.
- **Confidence**: settled (documented config artifacts)
- **Quote**: "**Cursor**: Create `.cursor/mcp.json` in your project root" and
  "Restart your AI tool after adding the configuration."
- **Our assessment**: The config is an executable contract: `command: "npx"`,
  `args: ["promptfoo@latest", "mcp", "--transport", "stdio"]`. Installing the
  integration is therefore granting the client permission to spawn a process
  (the same shape as the MCP STDIO command-injection class documented in
  `failure-litellm-mcp-stdio-command-injection.md`, though here the user is
  the one choosing the command). For Ch03/Ch06, treat a checked-in
  `.cursor/mcp.json` as reviewable code — it names a binary the editor will
  run on every session.

### Claim 13: Red-team execution (`redteam_generate`, `redteam_run`) is agent-callable, and the page offers no target authorization, scope, or blast-radius guidance beyond "start basic" and "review generated test cases"
- **Evidence**: The two red-team tool descriptions plus the "Security First"
  best-practice block; the security-testing example workflow runs
  `redteam_generate` → `redteam_run` → `get_evaluation_details` with no
  approval step.
- **Confidence**: emerging (the tools and workflow are settled; the absence of
  scope guidance is an argument from silence)
- **Quote**: "**`redteam_generate`** - Generate adversarial test cases for
  redteam security testing with configurable plugins and strategies" and
  "Always analyze results thoroughly"
- **Our assessment**: Ch06 recommends red-teaming as a CI gate; this page shows
  the same capability offered as an agent-invoked tool. The doc assumes the
  operator owns the target and has already scoped the scan. There is no
  allowlist of targets, no confirmation before attack traffic, and no cost
  bound beyond the tool's arguments. Treat agent-invoked `redteam_run` as a
  write-class action against an external system: require an explicit target
  list and human approval, and keep the run's transcripts for comparison.

## Concrete Artifacts

Transport launch commands (source: promptfoo MCP Server page, "1. Start the
Server"; code blocks arrive collapsed after HTML extraction — line breaks
restored at command boundaries only, no wording changes):

```bash
# For Cursor, Claude Desktop (STDIO transport)
npx promptfoo@latest mcp --transport stdio

# For web tools (HTTP transport)
npx promptfoo@latest mcp --transport http --port 3100
```

Cursor project config — `.cursor/mcp.json` (source: same page, "2. Configure
Your AI Tool"; line breaks/indentation restored, values verbatim):

```json
{
  "mcpServers": {
    "promptfoo": {
      "command": "npx",
      "args": ["promptfoo@latest", "mcp", "--transport", "stdio"],
      "description": "Promptfoo MCP server for LLM evaluation and testing"
    }
  }
}
```

Claude Desktop config (source: same page; identical block is shown for all
three documented paths — macOS `~/Library/Application Support/Claude/claude_desktop_config.json`,
Windows `%APPDATA%\Claude\claude_desktop_config.json`, Linux
`~/.config/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "promptfoo": {
      "command": "npx",
      "args": ["promptfoo@latest", "mcp", "--transport", "stdio"],
      "description": "Promptfoo MCP server for LLM evaluation and testing"
    }
  }
}
```

Full tool catalog (source: same page, "Available Tools"; names and one-line
descriptions verbatim):

```
Core Evaluation Tools
  list_evaluations        - Browse your evaluation runs with optional dataset filtering
  get_evaluation_details  - Get comprehensive results, metrics, and test cases for a specific evaluation
  run_evaluation          - Execute evaluations with custom parameters, test case filtering, and concurrency control
  share_evaluation        - Generate publicly shareable URLs for evaluation results

Generation Tools
  generate_dataset        - Generate test datasets using AI for comprehensive evaluation coverage
  generate_test_cases     - Generate test cases with assertions for existing prompts
  compare_providers       - Compare multiple AI providers side-by-side for performance and quality

Redteam Security Tools
  redteam_run             - Execute comprehensive security testing against AI applications with dynamic attack probes
  redteam_generate        - Generate adversarial test cases for redteam security testing with configurable plugins and strategies

Configuration & Testing
  validate_promptfoo_config - Validate configuration files using the same logic as the CLI
  test_provider             - Test AI provider connectivity, credentials, and response quality
  run_assertion             - Test individual assertion rules against outputs for debugging
```

HTTP JSON-RPC example (source: same page, "Custom HTTP Integrations"; code
block arrives as one collapsed line — line breaks restored at JS boundaries,
no wording changes):

```javascript
// Example: Call MCP server from Node.js
const response = await fetch('http://localhost:3100/mcp', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    method: 'tools/call',
    params: {
      name: 'list_evaluations',
      arguments: { datasetId: 'my-dataset' },
    },
  }),
});
```

Environment variables (source: same page, "Environment Variables"; verbatim):

```bash
# Set provider API keys
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...

# Configure promptfoo behavior
export PROMPTFOO_CONFIG_DIR=/path/to/configs

# Start server with environment
npx promptfoo@latest mcp --transport stdio
```

Health check (source: same page, Troubleshooting → "AI tool can't connect"):

```bash
curl http://localhost:3100/health
```

Slim-install remedy (source: same page, Prerequisites and Troubleshooting;
verbatim):

```bash
npm install promptfoo @modelcontextprotocol/sdk
```

```bash
# Server won't start checks
npx promptfoo@latest --version
npx promptfoo@latest validate
npx promptfoo@latest mcp --transport stdio
```

Port-conflict checks (source: same page, "Port conflicts (HTTP mode)";
verbatim):

```bash
# Use a different port
npx promptfoo@latest mcp --transport http --port 8080

# Check what's using port 3100
lsof -i :3100           # macOS/Linux
netstat -ano | findstr :3100   # Windows
```

## Cross-References

- **Corroborates**:
  - `source-notes/docs-litellm-evals-api.md` **Claim 8** ("The page documents
    **no** authorization, tenancy, rate limit, quota, concurrency, retention,
    spend, cost, retry, or error contract for the evals surface") — the same
    documented gap in a different vendor's eval control plane. LiteLLM exposes
    evals as a gateway API; promptfoo exposes them as MCP tools. Neither page
    describes who may call the surface, which makes "eval execution is an
    unguarded control plane" a cross-vendor pattern in the corpus rather than
    a promptfoo quirk.
  - `source-notes/docs-promptfoo-configuration-tools.md` **Claim 1** ("Tool
    calling is a four-step loop in which the model emits a name and arguments
    and executes nothing — the harness (or the application) is the thing that
    runs code") — that note says declaring a tool in a promptfoo config is
    only a contract declaration. This page is the other side: promptfoo now
    ships the harness that *does* execute, and hands it to the agent. The
    trust boundary moves from "the model requested a call" to "the server ran
    it."
  - `source-notes/docs-promptfoo-enterprise-findings-reports.md` **Claim 10**
    ("The documented programmatic surface for findings is read-only — search
    via `GET /api/v1/results` and shareable URLs via `promptfoo share`") —
    this page makes the shareable-URL step an MCP tool (`share_evaluation`,
    Claim 4). The enterprise note's read-only surface assumption does not hold
    on the agent-facing path: an agent can publish, not just read.
  - `source-notes/failure-litellm-mcp-stdio-command-injection.md`
    **"Vulnerability Detail A"** (the `command` field passed straight through
    to `StdioServerParameters` and executed as a subprocess) and **"Fix Layer
    1"** (the `MCP_STDIO_ALLOWED_COMMANDS` launcher allowlist) — the security
    counterpoint for Claim 12. Promptfoo's STDIO config is exactly a
    user-authored `command`/`args` pair that the client executes; the
    difference is that here the user writes it knowingly. It still belongs in
    the same review: MCP STDIO configs are executable content.
- **Contradicts**: none found. Checked `CONTRADICTIONS.md` and open
  `contradiction`-labeled issues before writing. The nearest surface is a
  *tension*, not a contradiction: `docs-promptfoo-code-scan-github-action.md`
  Claim 3 documents the vendor hardening its other agent-facing artifact off
  runtime `promptfoo@latest`, while this page (Claim 7) still documents
  `promptfoo@latest` as the default MCP launch. Those are different artifacts
  and different trust assumptions (a CI action vs a developer's local MCP
  server), so this is a conditioning variable, not a same-topic disagreement.
  No contradiction issue filed.
- **Extends**:
  - `source-notes/docs-promptfoo-agent-skill.md` — the authoring-side sibling:
    its **Claim 1** covers the four-skill bundle that teaches an agent how to
    write and run promptfoo evals; this note covers the runtime MCP server
    that lets an agent invoke them. Same "let agents drive the eval harness"
    story, opposite ends: that note is *how to author*, this one is *what is
    exposed*. Its **Claim 5** (`--no-share` gates sharing, not egress) is the
    command-line counterpart to this page's `share_evaluation` (Claim 4).
  - `source-notes/docs-langfuse-mcp-server.md` — the corpus's other MCP-server
    note, useful as the auth contrast the Prospector asked for. Langfuse's
    docs MCP is unauthenticated but read-only public documentation (**Claim
    4**); its data-platform MCP is authenticated, project-scoped, and
    write-by-default (**Claims 8-9**). Promptfoo's MCP server is the missing
    middle: unauthenticated *and* capable of mutating/publishing, with provider
    credentials in process (Claims 3-6). Cite as a contrast, not a duplicate:
    Langfuse documents two auth postures, promptfoo documents none.
  - `source-notes/docs-promptfoo-evaluate-coding-agents.md` **Claim 13**
    ("Safety defaults for coding-agent evals treat the agent as arbitrary code
    execution — never production credentials, real customer data, or
    internal-network access") — the same vendor applies a strict sandbox
    posture when *it* runs an agent, while this page hands the eval control
    plane to an agent with no documented sandbox or auth. The asymmetry is
    worth preserving in Ch06: the harness's own adversarial assumptions do
    not automatically transfer to the harness-as-tool.
- **Novel** (first appearances in the corpus):
  1. An eval/red-team harness exposed as an agent-callable MCP tool surface
     (Claims 1-3) — prior MCP notes cover docs search and data-platform tools,
     not eval execution.
  2. `share_evaluation` as an agent-invokable publication step (Claim 4) — the
     corpus documents `promptfoo share` as a CLI/read-only surface but not as
     an MCP tool with no approval gate.
  3. The unauthenticated HTTP eval control plane: `/mcp` + `/health` with
     provider keys inherited from the environment (Claims 5-6, 11).
  4. The cwd-scoped eval store as an agent-runbook confounder (Claim 9) — no
     prior note treats "which directory the server started in" as the thing
     that determines which evals an agent can see.
  5. The slim-install `@modelcontextprotocol/sdk` failure mode and its
     version-resolution side effect (Claim 8).

## Guide Impact

- **Chapter 03 (Runbooks and Agents — "Read vs. write capabilities",
  `guide/03-runbooks-and-agents.md:140`)**: The section's rule is "Default-deny
  all write capabilities. Every write action requires explicit human
  approval." Add this page as the worked example of a tool surface that
  supplies **no read/write labels**: the twelve-tool catalog (Claim 2) mixes
  `list_evaluations` with `run_evaluation`, `redteam_run`, and
  `share_evaluation`, and the operator must build the split themselves
  (Claim 3). The actionable checklist: classify every exposed MCP tool into
  read / cost-incurring / externally-visible before granting the client
  access, and gate `share_evaluation` and `redteam_run` at minimum.
- **Chapter 03 ("The emerging agent control plane",
  `guide/03-runbooks-and-agents.md:332`)**: The section's four verbs are
  register, invoke, observe, govern. This page supplies *invoke* (run evals,
  generate datasets, run red-team scans) but no *govern* — no auth, no
  approval, no audit, no spend cap (Claims 3-6). Add a sentence: an
  agent-callable eval harness is a control plane in miniature; check that the
  exposed verbs include a governance path before treating it as production
  infrastructure. The page's only safety mechanism is ordering advice (Claim
  10), which is a prompt, not a policy.
- **Chapter 05 (LLM-ops reliability — "A gate that cannot fail is not a
  gate", `guide/05-llm-ops-reliability.md:655`)**: The section already requires
  explicit thresholds and a negative control. Add the agent-invoked path as a
  new failure mode: an agent can call `run_evaluation` directly, so the gate's
  integrity depends on *who* can trigger the run and *which* directory it ran
  in (Claim 9). Recommend: agents may read eval results and validate configs;
  full eval runs and publication stay behind CI or human approval; and the MCP
  server's cwd/config dir is pinned so a green run is measured against the
  intended suite. Use the page's own ordering (validate → test provider →
  subset → full, Claim 10) as the pre-deploy sequence the guide already
  recommends.
- **Chapter 05 ("Evaluation must stay separate from side effects",
  `guide/05-llm-ops-reliability.md:254`)**: This page is the counterexample the
  section needs: the eval control plane can generate datasets, publish
  results, and launch red-team traffic from the same agent session that is
  being evaluated (Claims 3-4). Add the rule that eval execution must be
  separated from eval publication and from agent self-triggering — an agent
  should not be able to run the suite that grades it and then share the
  result.
- **Chapter 06 (Security and Trust — "An agent gateway's default is full
  access", `guide/06-security-and-trust.md:316`)**: Add the HTTP transport as
  the MCP version of the same default: no authentication is documented for
  `/mcp` or `/health` (Claim 5), provider keys are inherited from the
  environment (Claim 6), and any JSON-RPC client can call `tools/call` (Claim
  11). Recommend binding to localhost, fronting with an authenticating proxy
  before any network exposure, and giving the server dedicated least-privilege
  provider credentials. Contrast explicitly with Langfuse's authenticated
  data-plane MCP so readers see both postures.
- **Chapter 06 ("Red-teaming as a CI gate",
  `guide/06-security-and-trust.md:120`)**: The chapter treats red-team scans as
  a CI gate; this page makes `redteam_run` and `redteam_generate` agent tools
  (Claim 13). Add a rule: an agent-invoked red-team run needs an explicit
  target allowlist and human approval, because the page supplies neither and
  its "Security First" advice is not enforced by the tool contract.
- **Chapter 06 ("Pin everything; verify releases",
  `guide/06-security-and-trust.md:636`)**: Use this page as the concrete
  counterexample to the pinning rule: both the documented launch and the
  checked-in client configs use `npx promptfoo@latest` (Claim 7). Add: pin the
  version inside the `mcpServers` `args` array and verify provenance, exactly
  as the code-scan action guidance already requires. The slim-install remedy
  (Claim 8) is a useful illustration that same-project resolution is the safer
  mode, even though the vendor documents it only as a troubleshooting step.

## Extraction Notes

- Source fetched in full via direct HTTP fetch of the Docusaurus page
  (https://www.promptfoo.dev/docs/integrations/mcp-server) on 2026-10-27;
  page footer "Last updated on **Oct 26, 2026** by **renovate\[bot\]**". No
  sub-pages were followed: the page is self-contained, and its outbound links
  (MCP protocol home, promptfoo docs home, examples directory) do not document
  this server's contract. Sibling promptfoo pages already have source notes
  and are cited instead of re-mined.
- Quotes verified character-for-character against the fetched rendered page
  before writing. Code blocks arrive as collapsed single lines after HTML
  extraction; line breaks/indentation were restored at command, JSON, JS, and
  list boundaries only, with no wording changes (same convention as the
  sibling promptfoo notes). The tool catalog artifact preserves the page's
  exact one-line descriptions and group headings; the alignment spaces are
  formatting only.
- **Arguments from silence are labeled as such**: the page never says "there
  is no authentication" or "results are never reviewed." Claims 3, 4, 5, and
  13 are graded emerging partly because they rest on absence of documentation.
  We deliberately did NOT assert that the HTTP server binds a public interface,
  that `share_evaluation` is unguarded in the implementation, or that
  `redteam_run` can attack arbitrary targets — only that the docs provide no
  auth, approval, or scope mechanism, and that the documented tools are
  callable directly. This mirrors the Prospector's instruction to flag the gap
  rather than assert a vulnerability.
- **Candidate disposition** (from `miner-related-notes.md`, read before
  Cross-References; every listed path cited or dismissed by name):
  - `docs-langfuse-mcp-server.md` — **cited** (Extends/contrast: no-auth docs
    MCP vs authenticated data-plane MCP; Claims 4 and 8-9).
  - `docs-litellm-evals-api.md` — **cited** (Corroborates, Claim 8: eval
    control plane with no documented authorization/rate/tenancy contract).
  - `docs-promptfoo-enterprise-findings-reports.md` — **cited** (Corroborates,
    Claim 10: `promptfoo share` as the CLI/publication counterpart).
  - `blog-pagerduty-sre-agent-triage.md` — dismissed: incident-triage agent
    consuming observability via MCP connectors (its Claim 4), with no eval
    harness, tool catalog, or transport/auth content.
  - `docs-google-sre-reliable-product-launches.md` — dismissed: launch-gating
    process chapter; no MCP, agent-tool, or eval-server content.
  - `docs-promptfoo-evaluate-coding-agents.md` — **cited** (Extends,
    Claim 13: the vendor's own sandbox posture for running agents, contrasted
    with handing its control plane to an agent).
  - `docs-promptfoo-evaluate-openai-agents-python.md` — dismissed: Python
    Agents SDK tracing/OTLP bridge; no MCP server, transport, or tool-catalog
    content.
  - `docs-litellm-batches-api.md` — dismissed: batch rate-limit accounting;
    unrelated vendor and surface.
  - `docs-promptfoo-pi-scorer.md` — dismissed: a single model-graded scorer's
    mechanics; no MCP or agent-tool content.
  - `docs-google-sre-eliminating-toil.md` — dismissed: toil measurement and
    automation economics; no LLM eval-harness content.
- Additional cross-refs beyond the candidate list found by searching
  `source-notes/`: `docs-promptfoo-agent-skill.md`,
  `docs-promptfoo-configuration-tools.md`,
  `failure-litellm-mcp-stdio-command-injection.md`, and
  `docs-promptfoo-code-scan-github-action.md`. Every cited `Claim N` was
  re-read and verified against the cited note per MINER.md §4b before writing;
  the failure-report cite uses section names ("Vulnerability Detail A",
  "Fix Layer 1") because that note has no numbered claims.
- `confidence_overall: emerging` — the mechanics (tool names, transport flags,
  config artifacts, env inheritance, error strings, launch commands) are
  settled and checkable; the trust-boundary claims that matter most (read/write
  split, no auth, no approval gate, no scope guidance) rest on what the page
  omits, and the page reports no measurements of agent use. Per the
  Prospector's guidance, vendor-authoritative mechanics are graded settled at
  the fact level while the blast-radius reading stays emerging.
- No contradiction issue filed: checked `CONTRADICTIONS.md` and open
  `contradiction`-labeled issues; the pinning tension with
  `docs-promptfoo-code-scan-github-action.md` is a different-artifact
  conditioning variable, not a same-topic contradiction (see Cross-References).
- `registry/sources.json` and `registry/claims-index.json` were NOT edited —
  both are derived indexes rebuilt after merge.
