---
source_url: https://langfuse.com/docs/api-and-data-platform/features/cli
source_type: docs
title: "Langfuse CLI"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: "unknown (Langfuse vendor docs; page footer © 2022–2026; feature shipped 2026-02-17 per changelog image on page)"
date_extracted: 2026-08-29
last_checked: 2026-08-29
status: current
confidence_overall: settled
issue: "#1057"
---

# Langfuse CLI

> The vendor documentation for the Langfuse CLI — a terminal wrapper over the
> entire Langfuse REST API, generated from the OpenAPI spec, that inherits the
> same project API-key pair as the SDKs and documents a fixed, machine-readable
> exit-code scheme (usage/configuration/network/HTTP/local) so coding agents
> can classify failures "without parsing stderr." This is the third of the
> vendor's three agent-facing surfaces (alongside the MCP server #131 and the
> Agent Skill #1056) and the cleanest single example in the corpus of
> designing a data-plane CLI for machine consumption.

## Source Context

- **Type**: docs (vendor product documentation — feature page)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor documenting a shipped, inspectable artifact (`github.com/langfuse/langfuse-cli`).
  Claims about how the CLI authenticates, what it wraps, and its exit-code
  contract describe the shipped surface, so they are authoritative and factual
  (settled). The "built for AI coding agents and power users" positioning and
  the task-automation "why use it" bullets are vendor framing, not measured
  claims.
- **Scope**: Covers what the CLI is, the OpenAPI-generated command surface, the
  env-var-only auth model (no `login` step), the machine-readable exit-code
  scheme, the stated use cases (coding-agent management and scripted
  CI/CD automation), and the pairing with the Agent Skill. Does NOT cover
  individual command syntax (deferred to the linked CLI GitHub repo), the MCP
  server, or the Agent Skill in detail (each covered by sibling notes #131,
  #1056).

## Extracted Claims

### Claim 1: The Langfuse CLI wraps the entire Langfuse API and is explicitly built for "AI coding agents and power users who prefer the command line"
- **Evidence**: The page's opening definition, which names the CLI's audience
  and frames it as terminal access to the full API rather than a narrow helper.
- **Confidence**: settled
- **Quote**: "The Langfuse CLI wraps the entire Langfuse API so you can interact with Langfuse directly from the terminal. It is built for AI coding agents and power users who prefer the command line."
- **Our assessment**: Load-bearing fact: an LLM-observability vendor ships a
  first-class CLI whose *stated* primary audience is AI coding agents, not just
  human operators. This is the framing that makes the rest of the page an
  agent-ops artifact rather than a plain dev-tool doc.

### Claim 2: The CLI is generated from the full OpenAPI spec, so every API endpoint (traces, observations, prompts, datasets, scores, sessions, metrics, etc.) is exposed as a CLI command
- **Evidence**: A dedicated "What it can do" paragraph stating the generation
  mechanism and naming the endpoint families covered.
- **Confidence**: settled
- **Quote**: "It is generated from the full OpenAPI spec, so every endpoint (traces, observations, prompts, datasets, scores, sessions, metrics, and more) is available as a CLI command."
- **Our assessment**: The API-contract-as-CLI mechanism. The command surface is
  not hand-written — it is mechanically derived from the OpenAPI spec, so CLI
  coverage tracks API coverage exactly and stays current with spec changes. This
  is the same "MCP/REST-as-a-wrapper" theme seen in the MCP note (#131), applied
  to the shell: one generated CLI that mirrors the whole data plane.

### Claim 3: Failures exit with a machine-readable code so agents can classify what went wrong "without parsing stderr" — usage (2), configuration (3), network (4), HTTP failure (5), local errors (6)
- **Evidence**: A single declarative sentence in the "What it can do" section
  giving the full fixed exit-code table and its stated purpose.
- **Confidence**: settled
- **Quote**: "Failures exit with a machine-readable code, so agents can tell what went wrong without parsing stderr: usage (2), configuration (3), network (4), HTTP failure (5), and local errors (6)."
- **Our assessment**: The most transferable pattern on the page and the novel
  contribution the Prospector flagged. The vendor has codified a fixed error-taxonomy
  into exit codes so an agent can branch on failure *class* programmatically
  (usage vs config vs network vs HTTP vs local) instead of scraping free-text
  stderr. Structured error signaling is the direct, agent-ops contrast to CLIs
  that only print human-readable errors. The exact numeric scheme (2/3/4/5/6) is
  Langfuse-specific, but the *design contract* — "failures are machine-
  classifiable at the process boundary" — generalizes to any agent-toolable CLI.
  The only comparable scheme in the corpus is #553's ModelAudit exit codes
  (0/1/2), but those are scan-result semantics (clean/findings/operational
  error) for a CI/CD scanner, not a failure-class taxonomy for an agent-driven
  CLI; Langfuse's error-class classification is the novel part here.

### Claim 4: The CLI authenticates with the same project API-key pair as the SDKs and public API, exposed via environment variables, with no separate login step
- **Evidence**: The Authentication section: it reuses the project key pair
  ("Create a key pair under Project settings → API Keys"), reads `LANGFUSE_PUBLIC_KEY` /
  `LANGFUSE_SECRET_KEY` / `LANGFUSE_BASE_URL` env vars, and states there is no
  separate login.
- **Confidence**: settled
- **Quote**: "The CLI authenticates with the same project API-key pair you use for the Langfuse SDKs and public API." ... "The CLI picks these up automatically — there is no separate `login` step."
- **Our assessment**: Auth consistency is a real operational win: one credential
  surface (env vars) serves SDK, public API, and CLI, with region-specific hosts
  (EU/US/JP/HIPAA + self-hosted). No device-login or token dance, which keeps the
  CLI safely scriptable/non-interactive in CI where interactive auth would hang.
  "Keys are scoped to a single project" reinforces the per-project isolation also
  seen in the MCP auth model (#131).

### Claim 5: For tools that cannot run commands or install packages, the documented alternative is the MCP server — i.e., Langfuse routes between its agent-facing surfaces by capability (CLI for shell-capable agents, MCP for embedded/transport-only contexts)
- **Evidence**: The opening Popular-options note directly after the intro line,
  explicitly pointing command-less/package-less tools to the MCP server and
  noting both "provide access to Langfuse features beyond prompt management."
- **Confidence**: settled
- **Quote**: "For tools that cannot run commands or install packages, connect the Langfuse MCP server instead. Both provide access to Langfuse features beyond prompt management."
- **Our assessment**: This is the vendor's own capability-based routing rule across
  its three agent surfaces, matching #131's "skill over MCP when you have a shell"
  (#131 Claim 10) and #1056's framing of the CLI as what the skill uses "under the
  hood." Here the split is explicit: a CLI requires the ability to run commands /
  install packages; an MCP server does not. Captures the design decision any
  agent-tooling vendor must make when a "wrapper around the same API" is exposed
  through both a CLI and an MCP.

### Claim 6: The stated use cases are (a) letting a coding agent (Cursor, Claude Code, Windsurf, etc.) manage Langfuse from inside the editor, and (b) scripting workflows like exporting traces, batch-scoring, or syncing prompts across environments in CI/CD
- **Evidence**: The "Why use it" bulleted list, which names both the editor-agent
  use case and the CI/CD scripting use case with concrete examples.
- **Confidence**: settled
- **Quote**: "Let your coding agent manage Langfuse for you. Cursor, Claude Code, Windsurf, etc. can use the CLI to create datasets, pull traces, update prompts, and more without you leaving the editor." ... "Script your workflows. Automate repetitive tasks like exporting traces, batch-scoring, or syncing prompts across environments in CI/CD or bash scripts."
- **Our assessment**: These two use cases map directly onto the Prospector's
  extraction targets: (a) the editor-agent operability claim (agent-run dataset /
  trace / prompt operations in a dev harness — corroborates #1056's example-agent-
  prompt list), and (b) CLI-in-CI/CD data-plane automation (export traces,
  batch-scoring, cross-environment prompt sync) for Ch02/Ch03 workflow scripting.
  The vendor is explicitly positioning the CLI as the automation primitive for
  these ops workflows, not just interactive use.

### Claim 7: The CLI is designed to work together with the Agent Skill — the skill teaches agents how to discover endpoints, follow common workflows, and access documentation, all through the CLI
- **Evidence**: The "Pairs with Agent Skills" callout, plus a pointer to the
  "Langfuse for Agents" umbrella.
- **Confidence**: settled
- **Quote**: "The CLI is designed to work together with Agent Skills. The skill teaches agents how to discover endpoints, follow common workflows, and access documentation, all through the CLI."
- **Our assessment**: Corroborates #1056 Claim 9 (the skill page's "CLI the skill
  uses under the hood") from the CLI page's side. The division of labor is:
  skill = guidance/conditioning; CLI = the executable surface the skill drives.
  This is the third half of the vendor's three-way surface routing (CLI, MCP,
  skill) and confirms the CLI as the shared execution layer beneath the skill.

## Concrete Artifacts

### Auth — env-var setup (verbatim bash + region hosts, from the Authentication section)
```bash
export LANGFUSE_PUBLIC_KEY="pk-lf-..."
export LANGFUSE_SECRET_KEY="sk-lf-..."

# Region-specific host. Defaults to https://cloud.langfuse.com (EU).
# US:    https://us.cloud.langfuse.com
# Japan: https://jp.cloud.langfuse.com
# HIPAA: https://hipaa.cloud.langfuse.com
# Self-hosted: your own deployment URL.
export LANGFUSE_BASE_URL="https://cloud.langfuse.com"
```
Source: langfuse.com/docs/api-and-data-platform/features/cli (Authentication section).

### Get started — command and agent prompt (verbatim)
```bash
npx langfuse-cli api <resource> <action>
```
```markdown
please install langfuse-cli
```
Source: langfuse.com/docs/api-and-data-platform/features/cli (intro). The second
block is the page's suggested instruction to paste to a coding agent.

### Exit-code scheme (verbatim, from the "What it can do" section)
```
Failures exit with a machine-readable code, so agents can tell what went wrong
without parsing stderr: usage (2), configuration (3), network (4), HTTP failure
(5), and local errors (6).
```

### "Why use it" bullets (verbatim)
```
- Let your coding agent manage Langfuse for you. Cursor, Claude Code, Windsurf,
  etc. can use the CLI to create datasets, pull traces, update prompts, and more
  without you leaving the editor.
- Script your workflows. Automate repetitive tasks like exporting traces,
  batch-scoring, or syncing prompts across environments in CI/CD or bash scripts.
- Faster than the UI for quick lookups. Grab the last 5 traces, check a prompt
  version, or list scores in seconds.
```

## Cross-References

- **Corroborates**:
  - `docs-langfuse-agent-skill.md` (#1056) **Claim 9** (the skill page frames the
    CLI as "the CLI the skill uses under the hood", with the MCP server as an
    "alternative protocol-based approach for agents"). This note's Claim 7
    corroborates that same division of labor from the CLI page's own side ("The
    skill teaches agents how to discover endpoints ... all through the CLI").
  - `docs-langfuse-mcp-server.md` (#131) **Claim 10** (Langfuse recommends the
    Agent Skill over MCP for agents that can run shell/CLI tools). This note's
    Claim 5 is the other half of that routing decision — the CLI page itself
    points command-less tools to MCP — confirming a consistent capability-based
    surface-selection policy across all three pages.
  - `docs-langfuse-roadmap.md` (#320) **Claim 4** ("Improve the Langfuse CLI, MCP
    surfaces, and skill management so external agents can inspect data shape,
    query Langfuse efficiently, and execute workflows") and **Claim 5** (make the
    CLI and other integration points "boringly reliable"). The shipped CLI
    documented here is the realized version of that planned surface; the roadmap
    frames the CLI as a strategic agent-facing automation layer rather than a
    niche dev tool.
  - `docs-langfuse-sdk-overview.md` (#302) **Concrete Artifacts → Credentials /
    data regions configuration** — the SDK overview's credential snippet uses the
    same `LANGFUSE_SECRET_KEY` / `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_BASE_URL` env
    vars and the same EU/US/Japan/HIPAA region hosts that the CLI page documents
    (this note's Claim 4). The CLI and SDK share an auth surface; the CLI page
    states "the same project API-key pair you use for the Langfuse SDKs and
    public API."

- **Contradicts**: None. The CLI page describes the shipped terminal surface and
  asserts no claim opposing any existing note; the three-way surface framing
  (CLI / MCP / skill) is internally consistent and consistent with how the MCP
  (#131) and skill (#1056) pages describe each other. No contradiction issue
  filed.

- **Extends**:
  - `docs-langfuse-mcp-server.md` (#131) and `docs-langfuse-agent-skill.md`
    (#1056) — together these three notes now document the complete set of the
    vendor's agent-facing surfaces. #131 covered the authenticated data-plane
    MCP server and its stateless per-key auth; #1056 covered the Agent Skill and
    its packaging; this note adds the third leg (the CLI) and the vendor's
    explicit capability-based routing between them (Claim 5). The corpus now has
    all three halves.
  - `docs-langfuse-roadmap.md` (#320) — the roadmap's planned "improve the
    CLI" work (Claim 4/8) is now grounded: this note documents the shipped
    baseline those improvements build on.

- **Novel** (first appearances in the corpus):
  - **Machine-readable exit-code taxonomy for an agent-toolable CLI** (Claim 3)
    — a vendor-space, fixed error-class→exit-code mapping (`usage(2)/
    configuration(3)/network(4)/HTTP(5)/local(6)`) explicitly designed so an
    agent can classify failure "without parsing stderr." The corpus does contain
    one comparable scheme — `blog-promptfoo-open-sourcing-modelaudit.md` (#553)
    documents a fixed CI/CD exit-code contract (0 = no issues, 1 = findings,
    2 = operational errors, in its Concrete Artifacts → "CI/CD integration exit
    codes" section) — but those are scan-result/pass-fail semantics, not a
    failure-class taxonomy. The novel part here is classifying *what kind* of
    failure occurred (usage vs config vs network vs HTTP vs local) so an agent
    can branch on error class at the process boundary, rather than just pass/
    fail/operational. This is the page's central novel contribution.
  - **OpenAPI-generated CLI-to-data-plane coverage** (Claim 2) — a CLI whose
    command surface is mechanically generated from the full OpenAPI spec so CLI
    coverage mirrors the API exactly. Extends the corpus's existing
    "MCP/REST-as-a-wrapper" theme (#131 Claim 6) to the shell.
  - **Env-var-only, non-interactive auth for a data-plane CLI** (Claim 4) — no
    `login` dance, safe to script — recorded as a concrete operator artifact.
  - **The vendor's three-way surface-routing rule** (Claim 5) — "need to run
    commands/packages → CLI; can't → MCP; want guidance → skill" — captured as a
    single decision rule.

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: This is the primary target. Add a
  subsection on **designing agent-toolable CLIs** using the Langfuse exit-code
  scheme (Claim 3) as the worked example: a fixed, documented error-class→exit-
  code contract so a runbook/agent can branch on failure class ("usage vs
  config vs network vs HTTP vs local") without parsing stderr. This generalizes
  beyond Langfuse: any CLI an agent (or an automated runbook) will invoke should
  signal failure *class* at the process boundary, the way Langfuse does, rather
  than relying on human-readable stderr. Pair with the OpenAPI-generated
  full-coverage surface (Claim 2) — "if you expose a data plane to agents,
  expose the whole API via a generated CLI, not a hand-picked subset." This is
  new content; the chapter currently covers harness configuration and agent
  dependencies but not structured CLI error signaling.

- **Chapter 02 (Observability)**: Add a short note that observability vendors
  expose the *data plane* to automation through a CLI wrapping the whole API
  (traces, observations, prompts, datasets, scores, sessions, metrics) using the
  same env-var auth as the SDKs (Claims 1, 2, 4). This complements the existing
  Ch02 coverage of SDK and MCP access to Langfuse data: an SRE can now export
  traces / batch-score / sync prompts in scripts without the SDK or UI. Keep it
  brief — the strong operational content (batch-scoring, prompt sync, trace
  export) is the scripting pattern, not the vendor marketing.

- **Chapter 05 (LLM Ops Reliability)**: Add the exit-code contract as an example
  of structured failure signaling for CI/CD orchestration (Claim 3, and Claim
  6's "Script your workflows" bullets). The specific claim — an agent can "tell
  what went wrong without parsing stderr" — is a reliability-relevant pattern
  for automated eval/observability gates in a pipeline, where exit status must
  drive branch logic. Contrast with tools that only emit human-readable errors
  (the Prospector's "design your agent-facing CLI for machine consumption"
  framing).

- **Not recommended**: Do not treat the page as evidence of Langfuse v4
  performance ("up to 165× faster" appears in vendor marketing, not on this
  page), and do not over-read the "built for AI coding agents" positioning as a
  measured claim — it is vendor framing. This is a thin docs page; cite it for
  the concrete exit-code contract, the OpenAPI-generated coverage mechanism, and
  the three-surface routing rule (Claims 2, 3, 5), not for effectiveness claims.

## Extraction Notes

- Source fetched 2026-08-29 via WebFetch (markdown rendering of the docs page).
  The page rendered cleanly (static Markdown prose); the trailing "Agent
  Instructions" block is boilerplate appended to every Langfuse docs page and was
  treated as incidental context, not extraction material.
- Per MINER.md §1, the substantive linked resource is the dedicated CLI GitHub
  repo (`github.com/langfuse/langfuse-cli`) named by the page as "the full
  documentation." It was not followed in depth: the individual command/readme
  detail it holds is scope-beyond-this-note (per the Prospector's triage, the
  extraction targets are the exit-code contract, the OpenAPI-generated surface,
  and the auth model — all on the page itself). The linked MCP server and Agent
  Skill pages are covered by sibling notes #131 and #1056 and were not re-followed.
- `confidence_overall: settled` — the claims describe a shipped, first-party
  vendor surface (auth env vars, OpenAPI generation, exit-code contract), which
  is authoritative and factual, following the convention in the sibling Langfuse
  notes (#131, #302, #1056). The *pattern value* (e.g., "does a machine-readable
  exit code actually make agents more reliable?") is not measured on this page
  and is not asserted as proven — it is presented as the documented design
  contract.
- The Prospector flagged the marketing phrase "up to 165× faster" as NOT to be
  extracted — confirmed: that claim is not on this page (it belongs to general
  Langfuse v4 marketing), so it is excluded.
- miner-related-notes.md candidates processed (cite or dismiss each):
  - `docs-langfuse-mcp-server.md` (#131) — **Cited** (Corroborates routing
    Claim 5/#131 Claim 10; Extends — third of the three-agent-access surfaces).
  - `docs-langfuse-agent-skill.md` (#1056) — **Cited** (Corroborates Claim 7 /
    #1056 Claim 9; Extends — skill-and-CLI pairing).
  - `docs-langfuse-roadmap.md` (#320) — **Cited** (Corroborates Claims 4/5 —
    CLI as strategic external-agent and reliability surface).
  - `docs-langfuse-sdk-overview.md` (#302) — **Cited** (Corroborates Claim 4 —
    shared env-var credential model / region hosts).
  - `docs-langfuse-security-and-guardrails.md` — **Dismissed**. Guardrail-scanner
    pipeline; no CLI-surface overlap.
  - `docs-langfuse-glossary.md` (#255) — **Dismissed**. Telemetry data model
    (traces/observations/scores); no CLI or agent-surface content.
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — **Dismissed**.
    Imperative-vs-declarative change workflows; unrelated to CLI error signaling.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — **Dismissed**.
    Autonomy levels and governance model; different layer of the stack, no CLI
    contract claims.
  - `docs-google-sre-data-processing-pipelines.md` — **Dismissed**. Pipeline
    SLOs and data-correctness; no CLI/exit-code content. (Mentally kept as a
    possible future Ch05 hook for batch-scoring scripting, but not cited.)
  - `docs-langfuse-evaluation-core-concepts.md` (#195) — **Dismissed**. Eval
    closed-loop/scores; the CLI page's eval relevance is indirect (batch-scoring
    via CLI), not a claim-level overlap.
  Additional manual search of `source-notes/`: the four Langfuse sibling notes
  above plus the MCP/skill pair were the substantive cross-refs. The `failure-*`
  notes have no CLI-surface claims to compare. One `blog-*` note does: #553
  (ModelAudit) documents a fixed CI/CD exit-code scheme (0/1/2) in its Concrete
  Artifacts that is directly comparable to Claim 3 — cited in the Novel entry,
  where it is distinguished from Langfuse's error-class taxonomy.
- No contradiction with existing notes surfaced (see Contradicts), so no
  contradiction issue was filed.
