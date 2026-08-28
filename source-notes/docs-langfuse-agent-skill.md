---
source_url: https://langfuse.com/docs/api-and-data-platform/features/agent-skill
source_type: docs
title: "Langfuse Agent Skill"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: "unknown (Langfuse vendor docs; page footer © 2022–2026)"
date_extracted: 2026-08-28
last_checked: 2026-08-28
status: current
confidence_overall: settled
issue: "#1056"
---

# Langfuse Agent Skill

> A static docs page from an LLM-observability vendor documenting its shipped
> Agent Skill — a self-contained `SKILL.md` + `references/` folder that follows
> the open Agent Skills standard and conditions coding agents toward Langfuse
> best practices (instrumentation, prompt management, datasets, eval) via
> progressive disclosure and CLI-driven access. The identifiable, third-party
> instantiation of the standard that `blog-anthropic-agent-skills.md` (#608)
> explicitly does not cover.

## Source Context

- **Type**: docs (vendor product documentation — feature page)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor documenting a live, open-source artifact (`github.com/langfuse/skills`,
  MIT-licensed, 262 stars / 34 forks at extraction). Claims about the skill's
  layout, install surface, and load semantics describe an inspectable shipped
  artifact, so they are authoritative and factual (settled). The one
  effectiveness claim ("significantly better results") is vendor assertion with
  no metrics and is graded `emerging` individually.
- **Scope**: Covers why the skill exists, the packaging layout (SKILL.md +
  progressive-disclosure `references/`), install mechanics (skills CLI, Cursor
  plugin, manual clone+symlink), and example agent prompts. Does NOT cover the
  Langfuse CLI itself (sibling page #1057, triaged separately) or the MCP
  server (sibling #1058 / existing note #131).
- **Sub-pages followed** (per MINER.md §1): the linked open-source repo
  `github.com/langfuse/skills` — README (install surfaces, `/add-plugin langfuse`,
  prerequisites) and the actual `skills/langfuse/SKILL.md` + `references/`
  folder listing, which verify the layout and supply the frontmatter and
  reference-file artifacts extracted below. The docs-page FileTree names three
  reference files (`cli.md`, `instrumentation.md`, `prompt-migration.md`, `...`);
  the live repo `references/` folder holds 15 files, confirming the "..." means
  more.

## Extracted Claims

### Claim 1: The Langfuse Agent Skill is a documented implementation of the open Agent Skills standard, shipped by an observability vendor for coding agents (Claude Code, Cursor, Windsurf, and other compatible agents), and is open source on GitHub
- **Evidence**: The page's opening definition; the artifact is a public MIT-
  licensed repo (`langfuse/skills`).
- **Confidence**: settled
- **Quote**: "The Langfuse agent skill helps AI coding agents use Langfuse effectively. It follows the open Agent Skills standard and works with Claude Code, Cursor, Windsurf, and other compatible agents. The skill is open source on GitHub."
- **Our assessment**: This is the load-bearing fact of the page: a concrete,
  non-Anthropic production implementation of the December 2025 open standard
  (#608). It makes the standard observable from a vendor's side — the exact
  comparison point the Anthropic post's scope section said it does not cover.

### Claim 2: The skill's stated rationale is conditioning — a coding agent with the skill installed is conditioned to follow Langfuse's best practices, which the vendor asserts produces significantly better results
- **Evidence**: The "Why use it" section. It is an opinionated claim with no
  metrics, benchmarks, or user studies attached.
- **Confidence**: emerging
- **Quote**: "Coding agents produce significantly better results with the skill installed, because they are conditioned to follow best practices. A coding agent with access to the skill has an opinionated view on what good looks like, based on Langfuse's knowledge."
- **Our assessment**: The mechanism being claimed — skills as a way to
  *condition* agents toward a vendor's notion of best practice — is a
  distribution-of-runbook/observability-knowledge argument (see PagerDuty
  cross-ref, Claim 3). But "significantly better results" is unmeasured
  marketing-grade assertion; take the mechanism, not the magnitude.

### Claim 3: The skill is a self-contained folder with a SKILL.md entrypoint and a references/ folder of per-workflow reference docs filled with specific best practices
- **Evidence**: The page's description plus the FileTree diagram; confirmed
  against the live repo (`skills/langfuse/SKILL.md` + `skills/langfuse/references/`).
- **Confidence**: settled
- **Quote**: "The skill is a self-contained folder with a `SKILL.md` entrypoint describing general rules and instructions on using documentation, plus reference docs for specific workflows that are filled with specific best practices"
- **Our assessment**: Matches the standard's anatomy (#608, Claims 2 and 4).
  The reference work is where the vendor packs its operational knowledge: the fed
  repo `references/` folder holds 15 files (cli, instrumentation,
  prompt-engineering, prompt-migration, create-dataset, setting-up-evals,
  judge-calibration, error-analysis, user-feedback, ci-cd, sdk-upgrade,
  trace-evaluator-upgrade, v4-project-migration, skill-feedback, etc.) — i.e.,
  one reference per runbook-style workflow.

### Claim 4: The skill uses a progressive disclosure model — the frontmatter is always loaded into the agent's context so it knows when the skill applies, while the full instructions and reference docs load only on demand, keeping context usage low
- **Evidence**: A dedicated paragraph in the "Why use it" section.
- **Confidence**: settled
- **Quote**: "The skill uses a progressive disclosure model: the frontmatter is always loaded into the agent's context so it knows when the skill is relevant, but the full instructions and reference docs are only loaded on demand. This keeps context usage low while giving agents access to specialized knowledge."
- **Our assessment**: This is the standard's level-1 (frontmatter/metadata always
  in context) and level-2/3 (body and linked files on demand) behavior (#608,
  Claims 3–4), described in the vendor's own two-stage formulation. No divergence
  in load semantics; the vendor just compresses the three levels into
  frontmatter-vs-rest.

### Claim 5: The primary install surface is the npm skills CLI — `npx skills add langfuse/skills --skill "langfuse"` — optionally targeting a specific agent with `--agent "<agent-id>"`
- **Evidence**: Verbatim bash in the "Install" section's third tab.
- **Confidence**: settled
- **Quote**: "npx skills add langfuse/skills --skill \"langfuse\""
- **Our assessment**: The `--skill "langfuse"` flag (subfolder selection inside
  the monorepo) and `--agent` targeting are distribution mechanics deeper than
  anything in #608's standard writeup. Worth preserving as concrete install
  artifacts.

### Claim 6: For agents without the skills CLI, the documented alternative is a manual install — clone the repo to a stable path, create the agent's skills root, then symlink the skill folder into it
- **Evidence**: An "Alternatively you can manually clone the skill" disclosure
  with three numbered steps (clone, `mkdir -p`, `ln -s`).
- **Confidence**: settled
- **Quote**: "Alternatively you can manually clone the skill"
- **Our assessment**: This is the standard's filesystem semantics made explicit
  for operators: a skill is just a directory, so a symlink is the install. The
  concrete commands are captured in Concrete Artifacts.

### Claim 7: Langfuse ships a Cursor Plugin that includes the skill automatically, and also supports agent-driven self-install by pointing the agent at the GitHub repository
- **Evidence**: A dedicated "Cursor plugin" install tab and the "Ask your coding
  agent" tab with an agent instruction string; the repo README confirms the
  plugin (`/add-plugin langfuse`).
- **Confidence**: settled
- **Quote**: "Langfuse has a [Cursor Plugin](https://cursor.com/docs/plugins) that includes the skill automatically."
- **Our assessment**: Two cheap distribution channels that need no npm: a
  marketplace plugin and a one-line natural-language instruction the user can
  paste to their coding agent.

### Claim 8: The documented example agent prompts are agent-run observability and prompt-management operations — trace-level score queries, dataset construction, and migrating a prompt out of the codebase into Langfuse prompt management
- **Evidence**: A bulleted "a couple of examples" list of prompts.
- **Confidence**: settled
- **Quote**: "Migrate the system prompt in src/agent.ts to Langfuse prompt management"
- **Our assessment**: These are concrete templates for agent-executed SRE-flavored
  work on an LLM platform ("show me the last 10 traces with a score below 0.5";
  "create a dataset … and add these 3 items"). See Concrete Artifacts for the
  full list. They pair with the ops-workflow list in #320's roadmap note.

### Claim 9: Langfuse frames its own CLI as what the skill uses "under the hood" and its MCP server as an "alternative protocol-based approach for agents" — i.e., skill and MCP are parallel agent-access surfaces with the skill positioned for agents that can run CLI tools
- **Evidence**: The "Resources" list's descriptions of the CLI and MCP pages.
- **Confidence**: settled
- **Quote**: "[Langfuse CLI](/docs/api-and-data-platform/features/cli) — the CLI the skill uses under the hood" and "[MCP Server](/docs/api-and-data-platform/features/mcp-server) — alternative protocol-based approach for agents"
- **Our assessment**: Corroborates at the skill page's level what #131 Claim 10
  already recorded from the authenticated MCP page ("If you are running AI agents
  in an environment where you can install CLI tools and run bash commands, we
  recommend using the Langfuse Agent Skill instead of the MCP server"). This page
  is the skill-side half of that recommendation.

### Claim 10: The skill's SKILL.md carries an `allowed-tools` frontmatter field that scopes the exact tool calls the agent may use to Langfuse surfaces — WebFetch on langfuse.com, curl to langfuse.com, and a bounded set of `npx langfuse-cli api ...` patterns
- **Evidence**: The YAML frontmatter of the live `skills/langfuse/SKILL.md`
  (linked repo, followed page), which lists `allowed-tools` beneath `name` and
  `description`.
- **Confidence**: settled
- **Quote**: "allowed-tools:" (the full allowlist is reproduced verbatim in
  Concrete Artifacts → SKILL.md frontmatter)
- **Our assessment**: A packaging-level security extension beyond the standard's
  required `name`/`description` frontmatter (#608, Claim 2): the vendor ships a
  self-imposed, read-leaning permission allowlist so the skill's blast radius on
  the user's shell is bounded at authoring time. Directly relevant to the
  skills-security discussion (#608, Claim 10).

### Claim 11: The SKILL.md encodes "Documentation First" as its first core principle — agents must never implement Langfuse integration from memory and must fetch current docs before writing code, because Langfuse updates frequently
- **Evidence**: The "Core Principles" list in the live SKILL.md (followed page),
  the first of five numbered principles.
- **Confidence**: settled
- **Quote**: "1. **Documentation First**: NEVER implement based on memory. Always fetch current docs before writing code (Langfuse updates frequently) See the section below on how to access documentation."
- **Our assessment**: A vendor encoding staleness-avoidance as a skill rule. It is
  the operational echo of the docs-as-a-constant-refetch pattern and pairs with
  the skill's three-method docs-retrieval workflow (Claim 12). The "Use latest
  Langfuse versions" rule is a sibling principle — version pinning as explicit
  best practice.

### Claim 12: The skill encodes a three-method documentation-retrieval workflow — llms.txt index for orientation, page-as-markdown (.md suffix or `Accept: text/markdown`) for a known page, and the semantic `search-docs` API as a fallback — with the practical rule that changelog posts confirm features but must never be implemented from
- **Evidence**: The "Langfuse Documentation" section of the live SKILL.md
  (followed page), methods 2a/2b/2c.
- **Confidence**: settled
- **Quote**: "Returns a structured list of every doc page with titles and URLs. Use this to discover the right page for a topic, then fetch that page directly."
- **Our assessment**: Same `search-docs` REST primitive (#131, Claim 6) surfaced
  through the skill. Notable that the tail of the docs page's own "Agent
  Instructions" block reproduces exactly this workflow for downstream agents — the
  vendor dogfoods its skill's retrieval pattern on every docs page.

## Concrete Artifacts

### Packaging layout — from the docs page FileTree (attribution: langfuse.com/docs/api-and-data-platform/features/agent-skill)
```
<FileTree>
  <FileTree.File name="SKILL.md" />
  <FileTree.Folder name="references" defaultOpen>
    <FileTree.File name="cli.md" />
    <FileTree.File name="instrumentation.md" />
    <FileTree.File name="prompt-migration.md" />
    <FileTree.File name="..." />
  </FileTree.Folder>
</FileTree>
```

### Actual `references/` folder in the live repo (attribution: github.com/langfuse/skills, `skills/langfuse/references/`)
```
ci-cd.md  cli.md  create-dataset.md  error-analysis.md  instrumentation.md
judge-calibration.md  prompt-engineering.md  prompt-migration.md  sdk-upgrade.md
setting-up-evals.md  skill-feedback.md  trace-evaluator-upgrade.md  user-feedback.md
v4-project-migration.md
```

### Install — skills CLI (verbatim bash, docs page)
```bash
npx skills add langfuse/skills --skill "langfuse"
```
Per-agent targeting:
```bash
npx skills add langfuse/skills --skill "langfuse" --agent "<agent-id>"
```

### Install — manual clone + symlink (verbatim bash, docs page)
```bash
git clone https://github.com/langfuse/skills.git /path/to/langfuse-skills
mkdir -p /path/to/<agent-skill-root>/skills
ln -s /path/to/langfuse-skills/skills/langfuse /path/to/<agent-skill-root>/skills/langfuse
```

### Install — Cursor plugin (docs page) and agent instruction (docs page, verbatim)
```
/add-plugin langfuse          # from the langfuse/skills README
```
Agent instruction to paste to a coding agent:
```txt
"Install the Langfuse Agent Skill from github.com/langfuse/skills."
```

### Example agent prompts (verbatim, docs page)
> "Once installed, you can prompt your agent with what you want to do. A couple
> of examples:"
```
- Show me the last 10 traces with a score below 0.5
- Create a dataset called "edge-cases" and add these 3 items to it
- Migrate the system prompt in src/agent.ts to Langfuse prompt management
```

### SKILL.md frontmatter (verbatim, attribution: github.com/langfuse/skills — `skills/langfuse/SKILL.md`)
```yaml
---
name: langfuse
description: >-
  Interact with Langfuse and access its documentation: tracing, monitoring, creating datasets, running experiments, and evaluating AI applications. Use when needing to (1) query or modify Langfuse data, (2) look up Langfuse documentation, concepts, integration guides, a feature or SDK usage, or (3) do any AI engineering task (AI observability, prompt engineering/management, evaluation and evaluator management, experimentation, dataset management, evaluation-driven CI/CD, feedback collection). Invoke it for tasks in this scope even when Langfuse is not configured or explicitly mentioned.
allowed-tools:
  - WebFetch(domain:langfuse.com)
  - Bash(curl *langfuse.com/*)
  - Bash(npx langfuse-cli api __schema *)
  - Bash(npx langfuse-cli api * --help *)
  - Bash(npx langfuse-cli api * list *)
  - Bash(npx langfuse-cli api * get *)
  - Bash(bunx langfuse-cli api __schema *)
  - Bash(bunx langfuse-cli api * --help *)
  - Bash(bunx langfuse-cli api * list *)
  - Bash(bunx langfuse-cli api * get *)
---
```

### SKILL.md core principles (verbatim wording, markdown formatting stripped; attribution: github.com/langfuse/skills — `skills/langfuse/SKILL.md`)
```
1. Documentation First: NEVER implement based on memory. Always fetch current
   docs before writing code (Langfuse updates frequently) See the section below
   on how to access documentation.
2. CLI for Data Access: Use langfuse-cli when querying/modifying Langfuse data.
   See the section below on how to use the CLI.
3. Best Practices by Use Case: Read the relevant reference below use-case-specific
   guidelines before asking the user for more details or implementing.
4. Use latest Langfuse versions: Unless the user specified otherwise or there's a
   good reason, always use the latest version of Langfuse SDKs/APIs. Even if
   you're only creating a plan for another agent to execute, be explicit about
   the exact version to use.
5. If you guide the user through UI and are unsure about a label or location,
   inspect the user's screenshots or ask to see the relevant screen. Do not
   assume UI labels have the exact same names as API, SDK, or CLI fields.
```

### SKILL.md "Use case specific references" mapping (verbatim, attribution: github.com/langfuse/skills)
```
- instrumenting an existing function/application: references/instrumentation.md
- creating or getting to a good (evaluation) dataset: references/create-dataset.md
- migrating prompts from a codebase into Langfuse: references/prompt-migration.md
- creating or changing a prompt: references/prompt-engineering.md
- setting up evals from existing traces: references/setting-up-evals.md
- capturing user feedback as scores on traces: references/user-feedback.md
- further tips on using the Langfuse CLI: references/cli.md
- upgrading/migrating SDKs and preserving instrumentation: references/sdk-upgrade.md
- upgrading trace-level evaluators to observation/experiment evaluators:
  references/trace-evaluator-upgrade.md
- preparing a project for the v4 platform migration: references/v4-project-migration.md
- judge calibration (LLM-as-a-Judge reliability): references/judge-calibration.md
- systematic error analysis: references/error-analysis.md
- setting up CI/CD experiment gates with langfuse/experiment-action:
  references/ci-cd.md
- submitting feedback about this skill: references/skill-feedback.md
```

### Docs-retrieval commands the skill prescribes (verbatim, attribution: github.com/langfuse/skills)
```bash
curl -s https://langfuse.com/llms.txt                     # orientation: full page index
curl -s "https://langfuse.com/docs/observability/overview.md"  # page-as-markdown
curl -s "https://langfuse.com/api/search-docs?query=<url-encoded-query>"  # semantic fallback
```
SKILL.md rule: "changelog posts may also surface here: use them only to confirm a
feature exists, never to implement from — their examples may be outdated".

## Cross-References

- **Corroborates**:
  - `blog-anthropic-agent-skills.md` (#608) **Claim 2** (a skill is a directory
    with a SKILL.md carrying YAML frontmatter) and **Claims 3–4** (progressive
    disclosure: metadata always loaded for relevance; body/linked files on
    demand). The Langfuse skill's `SKILL.md`+`references/` layout and "frontmatter
    is always loaded … full instructions and reference docs are only loaded on
    demand" statement (Claims 3–4 here) are the standard's anatomy implemented by
    a third party.
  - `docs-langfuse-mcp-server.md` (#131) **Claim 10** (Langfuse recommends its
    Agent Skill over the MCP server for agents that can run shell/CLI tools).
    This page is the skill-side primary source behind that recommendation: its
    Resources list frames the skill (CLI under the hood) against MCP as an
    "alternative protocol-based approach" (Claim 9 here).
  - `blog-pagerduty-sre-agent-triage.md` (#610) **Claim 3** (runbooks are encoded
    into the SRE Agent via skills — `create-pagerduty-skill` built from existing
    runbooks). Same mechanism, same claim: skills as the packaging unit for
    distributing runbook/operational knowledge to agents. Langfuse packages its
    own operational best practices as a skill; PagerDuty packages team runbooks
    as skills.
  - `docs-langfuse-roadmap.md` (#320) **Claim 4** (improve the CLI, MCP surfaces,
    and skill management so external agents can inspect data, query Langfuse, and
    execute workflows) and **Claim 8** ("automate repeated workflows through APIs,
    the CLI, skills, and an in-product agent"). The shipped skill is the `skills`
    leg of that planned surface already in production.

- **Contradicts**: None. The skill's packaging is consistent with the open
  standard it claims to follow (#608). The only delta is additive, not opposing:
  the `allowed-tools` frontmatter field (Claim 10) goes beyond the standard's
  required `name`/`description`, and the vendor's progressive-disclosure wording
  compresses the standard's three levels into frontmatter-always vs rest-on-demand
  (Claims 4) — a description simplification, not a load-semantics conflict. No
  contradiction issue filed.

- **Extends**:
  - `blog-anthropic-agent-skills.md` (#608) — fills the gap that post's scope
    section explicitly names ("comparison to other agent-packaging formats — MCP,
    Langfuse Skills, etc."): this note adds a real vendor implementation, its
    install mechanics (`npx skills add ... --skill "langfuse" [--agent <id>]`,
    Cursor plugin, clone+symlink), and the `allowed-tools` packaging extension.
  - `docs-langfuse-mcp-server.md` (#131) — the skill and the MCP server are the
    two halves of Langfuse's "help coding agents use Langfuse" surface; this page
    documents the skill half and the vendor's framing of the trade-off (CLI/skill
    vs protocol-based MCP).
  - `docs-langfuse-prompt-management.md` (#319) — the skill's
    `references/prompt-migration.md` codifies the exact prompt-management workflow
    that note documents (versioned prompts, decoupling prompt updates from code
    deploys), expressed as an agent-executable reference.
  - `docs-langfuse-roadmap.md` (#320) — the roadmap listed skill surfaces as a
    planned improvement loop; this page shows the shipped realization.

- **Novel** (first appearances in the corpus):
  - A **shipping third-party implementation of the open Agent Skills standard**
    by an observability vendor — the concrete "what does a real skill look like
    outside Anthropic" comparison point (Claims 1, 3).
  - The **`allowed-tools` frontmatter field** as a packaging-time tool-permission
    allowlist inside a skill (Claim 10) — a self-scoping security control beyond
    #608's trust-at-install guidance.
  - The **distribution surface**: skills CLI with per-agent targeting
    (`--agent <id>`), a Cursor marketplace plugin, agent self-install by
    instruction string, and clone+symlink (Claims 5–7).
  - **Skills as an observability vendor's best-practice distribution channel** —
    the claim that a skill "conditions" coding agents toward instrumentation and
    prompt-management norms (Claim 2), and the per-workflow `references/` content
    map (artifact) as a runbook-packaging template.
  - The **2-stage progressive-disclosure framing** ("frontmatter always loaded;
    instructions and references on demand") as the vendor's restatement of the
    standard (Claim 4).

## Guide Impact

- **Chapter 03 (Runbooks and Agents)**: Add the Langfuse Agent Skill as the
  concrete third-party worked example of the Agent Skills pattern from
  `blog-anthropic-agent-skills.md` (#608): the `SKILL.md` + `references/` layout
  (docs-page FileTree + the actual 15-file reference map as the artifact),
  the two-stage progressive-disclosure model, the `npx skills add
  langfuse/skills --skill "langfuse" [--agent <id>]` install command with manual
  clone+symlink fallback, and the example agent prompts ("show me the last 10
  traces with a score below 0.5", "migrate the system prompt in src/agent.ts to
  Langfuse prompt management") as templates for agent-run observability and
  prompt-management operations. Also: skills as a distribution mechanism for
  runbook/observability knowledge, corroborated by the PagerDuty
  `create-pagerduty-skill` pattern (#610).

- **Chapter 02 (Observability)**: Note that observability vendors are packaging
  agent-facing knowledge as skills, not just MCP servers — Langfuse ships both,
  with an explicit skill-vs-MCP framing ("CLI under the hood" vs "alternative
  protocol-based approach"). This complements the vendor-MCP coverage in
  `docs-langfuse-mcp-server.md` (#131) and the Datadog/Observability-MCP thread.

- **Chapter 06 (Security and Trust)**: Use the Langfuse `allowed-tools`
  frontmatter allowlist as a concrete packaging-time security control for skills —
  scoping exactly which WebFetch/Bash invocations an installed skill may run —
  which extends the trust-at-install guidance in #608 (Claim 10) with a
  self-limiting tool surface worth recommending for any skill author.

- **Not recommended**: Do not cite Claim 2 ("significantly better results") as
  evidence of skill effectiveness — it is a vendor assertion with no measurement.
  This page is setup/packaging documentation; its value is the concrete artifact
  surface and the standard-implementation comparison, not proof that skills work.

## Extraction Notes

- Source fetched 2026-08-28 via WebFetch (markdown rendering of the docs page).
  The page is the static prose for the Langfuse Agent Skill feature; its trailing
  "Agent Instructions" block is boilerplate appended to every Langfuse docs page
  and was used only as incidental context, not extracted.
- Per MINER.md §1, substantive linked pages were followed:
  1. `github.com/langfuse/skills` (the repo the page points at) — README install
     surfaces and `/add-plugin langfuse`; contributes Claim 7.
  2. `skills/langfuse/SKILL.md` (raw) — frontmatter (`name`, `description`,
     `allowed-tools`), Core Principles, docs-retrieval workflow; contributes
     Claims 10–12 and several Concrete Artifacts.
  3. `skills/langfuse/references/` (folder listing) — the actual 15 reference
     files behind the docs page's `...`; contributes artifacts and the per-
     workflow reference map.
  Not followed (sibling "#1057/#1058" triage boundary from the Prospector):
  the Langfuse CLI page (the skill's "under the hood" surface) and the MCP server
  page — both already covered by existing/existing notes and parallel issues; the
  note records only how this page *frames* them. The three linked Langfuse blog
  posts were not fetched (self-contained marketing/best-practice blog; not needed
  to verify the skill's mechanics).
- `confidence_overall: settled` — the claims describe a shipped, open-source,
  inspectable artifact; the frontmatter, install commands, and references listing
  were verified against the live repo at extraction time. Claims graded
  individually: Claim 2 is `emerging` (vendor effectiveness assertion, no
  metrics) while the packaging/mechanics claims are `settled`. This mirrors the
  convention in the sibling Langfuse docs notes (#131, #319).
- Packaging divergence check (per the Prospector's "flag if any packaging detail
  diverges from the standard" instruction): no divergence in directory layout or
  load semantics. Two deltas noted and captured in the body: the `allowed-tools`
  frontmatter extension (Claim 10) and the two-stage progressive-disclosure
  wording (Claim 4, consistent with the standard).
- miner-related-notes.md candidates processed (cite or dismiss each):
  - `docs-langfuse-mcp-server.md` — **Cited** (Corroborates Claim 10; Extends —
    the other half of the skill-vs-MCP surface).
  - `docs-langfuse-roadmap.md` — **Cited** (Corroborates Claims 4/8 — skills as
    a strategic external-agent surface).
  - `docs-langfuse-security-and-guardrails.md` — **Dismissed**. Guardrail-scanner
    pipeline; unrelated to agent-skill packaging.
  - `docs-langfuse-sdk-overview.md` — **Dismissed**. SDK instrumentation methods
    and OTel mapping; the skill *references* instrumentation as a workflow but the
    note's claims don't overlap.
  - `docs-langfuse-glossary.md` — **Dismissed**. Telemetry data model
    (traces/observations/scores); no skill-surface content.
  - `blog-pagerduty-sre-agent-triage.md` — **Cited** (Corroborates Claim 3 —
    skills as runbook-distribution mechanism).
  - `docs-google-sre-prodcast-03-13-imperative-declarative.md` — **Dismissed**.
    Imperative-vs-declarative change workflows; no agent-packaging overlap.
  - `docs-google-sre-ai-engineering-reliable-operations.md` — **Dismissed**.
    Autonomy levels and governance; different layer of the stack.
  - `docs-datadog-llm-observability.md` — **Dismissed**. Trace/span taxonomy;
    Datadog has no skill-surface claims to compare.
  - `docs-langfuse-evaluation-core-concepts.md` — **Dismissed** (also in the
    candidates list). Eval closed-loop/scores; the skill page's eval relevance is
    indirect (linked eval blog posts / settings-up-evals reference), not claims.
- Additional manual search of `source-notes/`: `docs-langfuse-prompt-management.md`
  (#319) **Cited** (Extends — the prompt-migration workflow the skill codifies).
  `blog-anthropic-agent-skills.md` (#608) **Cited** (Corroborates/Extends — the
  standard this implements). Other Langfuse sibling notes (compatibility, datasets,
  metrics-overview) were checked and **dismissed** — no skill-surface or packaging
  claims.
- No contradiction issue filed: no claim materially opposes an existing source
  note (see Contradicts). The `allowed-tools`/wording deltas are additive, not
  adversarial.