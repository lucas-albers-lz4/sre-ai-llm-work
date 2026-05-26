---
source_url: https://github.github.com/gh-aw/reference/workflow-structure
source_type: docs
title: "GitHub Agentic Workflows: Workflow Structure Reference"
author: GitHub Agentic Workflows team (GitHub Next / Microsoft Research)
date_published: null
date_extracted: 2026-05-26
last_checked: 2026-05-26
status: current
confidence_overall: emerging
issue: "#419"
---

# GitHub Agentic Workflows: Workflow Structure Reference

> The canonical reference specification for gh-aw workflow anatomy — documents
> the two-component file structure (YAML frontmatter + markdown body), directory
> conventions, the lock file metadata header format (`gh-aw-metadata`), the
> compile/runtime editability boundary, and naming best practices for workflow
> source files.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows `reference/workflow-structure`
  page — in the "Reference" section of the gh-aw documentation. This is the
  authoritative structural specification for what a workflow file contains
  and how it maps to compiled outputs. Distinct from: `docs-ghaw-how-they-work.md`
  (conceptual overview of the two-component model); `docs-ghaw-compilation-process.md`
  (technical pipeline inside `gh aw compile`); `docs-ghaw-frontmatter-full-reference.md`
  (complete YAML field catalog). This page is the "what does a workflow file
  look like" reference — structure, organization, naming, and the anatomy of
  both source and compiled files.)
- **Author credibility**: First-party from GitHub Next / Microsoft Research —
  the same team behind the `gh aw` CLI and Peli de Halleux's agent factory blog
  series. File layout conventions, lock file metadata format, and naming
  practices are authoritative for the `gh aw` platform. Claims are settled for
  this platform; they do not automatically generalize to other agentic
  workflow systems.
- **Scope**: Structural anatomy of gh-aw workflow files: the two-component
  model (YAML + markdown), directory organization in `.github/workflows/`,
  the lock file header format, the compile/runtime editability boundary, and
  file naming conventions. Does NOT cover: the full YAML frontmatter field
  catalog (see `docs-ghaw-frontmatter-full-reference.md`), the internal
  compilation pipeline phases (see `docs-ghaw-compilation-process.md`), the
  conceptual security model (see `docs-ghaw-how-they-work.md`), or specific
  workflow patterns and examples.

## Extracted Claims

### Claim 1: Each gh-aw workflow is a single file combining YAML frontmatter (configuration) and a markdown body (natural language instructions)

- **Evidence**: The page describes each workflow as containing two essential
  parts: "YAML Frontmatter: Configuration options wrapped in `---`" and
  "Markdown: Natural language instructions for the AI." A concrete minimal
  example demonstrates both parts in a single `.md` file (see Concrete
  Artifacts).
- **Confidence**: settled (first-party reference; the two-component structure
  is the foundational design of the platform)
- **Quote**: "YAML Frontmatter: Configuration options wrapped in `---`" and
  "Markdown: Natural language instructions for the AI"
- **Our assessment**: This page is the authoritative structural specification
  for the two-component model that `docs-ghaw-how-they-work.md` describes
  conceptually. The reference page adds concreteness: the YAML section is
  literally wrapped between `---` markers (standard YAML front matter), and
  the markdown section follows immediately after. The minimal example shows
  that a functional workflow can be very short — just an event trigger, a
  toolset, and a single natural language instruction sentence. For Ch02
  (Harness Engineering): this page is the structural reference to cite when
  explaining what a gh-aw workflow file looks like; `docs-ghaw-how-they-work.md`
  is the reference for *why* it is designed this way.

### Claim 2: Workflow source files live in `.github/workflows/` with `.md` extension; compilation generates a paired `.lock.yml` file with the same base name

- **Evidence**: The page documents the directory convention explicitly:
  `.github/workflows/` as the home for agentic workflows, with `.md` as the
  source extension and `.lock.yml` as the compiled output extension. The
  concrete example uses `ci-doctor.md` (labeled "Source agentic workflow")
  and `ci-doctor.lock.yml` (labeled "Compiled GitHub Actions Workflow") as
  the paired file pair within `.github/workflows/`.
- **Confidence**: settled (first-party reference; the file organization is
  a platform convention)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: The co-location of `.md` and `.lock.yml` in the same
  `.github/workflows/` directory is deliberate — it makes workflow evolution
  auditable in version control (both files change together when frontmatter
  is updated). The name pairing (`ci-doctor.md` → `ci-doctor.lock.yml`)
  makes it unambiguous which lock file corresponds to which source. For
  Ch02: recommend enforcing the name-pairing convention in code review —
  any `.md` workflow change that does not come with a corresponding
  `.lock.yml` update indicates a missed recompile.

### Claim 3: The `gh aw compile` command transforms a `.md` workflow source into a `.lock.yml` compiled GitHub Actions workflow

- **Evidence**: The page states `gh aw compile` as the compilation command
  and documents the transformation from `.md` source to `.lock.yml` output.
  The directory structure example explicitly labels the output as "Compiled
  GitHub Actions Workflow."
- **Confidence**: settled (first-party reference; the CLI command is
  documented and consistent with other reference pages)
- **Quote**: (no direct quote; see paraphrase in Our assessment)
- **Our assessment**: This corroborates the compilation model documented in
  `docs-ghaw-how-they-work.md` Claim 7 and `docs-ghaw-compilation-process.md`
  Claim 1. The structural reference page is the entry point for practitioners
  who need to understand the file artifacts before diving into the compilation
  internals. For Ch02: cite this page as the foundational reference for
  the `.md` → `.lock.yml` model; cite `docs-ghaw-compilation-process.md`
  for the internal five-phase pipeline.

### Claim 4: Lock files begin with a `gh-aw-metadata` comment line encoding `schema_version`, `frontmatter_hash`, `strict`, and `agent_id` as a machine-readable header

- **Evidence**: The page documents the lock file header format explicitly:
  `# gh-aw-metadata: {"schema_version":"v3","frontmatter_hash":"...","strict":true,"agent_id":"copilot"}`.
  The page notes this enables "reliable machine parsing" and that "subsequent
  sections document secrets and external actions used."
- **Confidence**: settled (first-party reference; the metadata header format
  is specifically documented as the standard lock file header)
- **Quote**: `# gh-aw-metadata: {"schema_version":"v3","frontmatter_hash":"...","strict":true,"agent_id":"copilot"}`
- **Our assessment**: The `gh-aw-metadata` header encodes four distinct pieces
  of information: (1) `schema_version` — which version of the lock file schema
  was used (currently v3), enabling forward-compatible tooling; (2)
  `frontmatter_hash` — a hash of the compiled frontmatter, which is how the
  platform detects whether recompilation is needed (a changed frontmatter
  produces a different hash, signaling drift between `.md` and `.lock.yml`);
  (3) `strict` — whether the workflow was compiled with `--strict` validation;
  (4) `agent_id` — the configured AI engine identity, embedded at compile time
  for auditability. The `frontmatter_hash` is particularly significant: it is
  the mechanism that makes the editability model (Claim 5) safe — the runtime
  can verify that the lock file was compiled from the current frontmatter before
  executing. For Ch02: the `gh-aw-metadata` header is the provenance record
  for a compiled workflow. Tools that read lock files should parse this header
  first. For Ch03 (Safety): `agent_id` embedding in the lock file means the
  intended model is captured as a compile-time artifact, enabling audit of
  what model ran a given workflow version.

### Claim 5: The markdown body can be edited directly on GitHub.com without recompilation; only frontmatter changes require running `gh aw compile`

- **Evidence**: The page states: "The markdown body is loaded at runtime and
  can be edited directly on GitHub.com without recompilation. Only frontmatter
  changes require recompilation."
- **Confidence**: settled (first-party; this is a stated design property and
  consistent with `docs-ghaw-compilation-process.md` Claim 7)
- **Quote**: "The markdown body is loaded at runtime and can be edited directly
  on GitHub.com without recompilation. Only frontmatter changes require
  recompilation."
- **Our assessment**: The editability model has practical implications for
  workflow iteration: instruction tuning (changing the natural language in the
  markdown body) has zero friction — no compile step, editable in the GitHub
  web UI. Structural changes (triggers, permissions, tools) require the compile
  step and a committed `.lock.yml` update. This creates two distinct iteration
  loops: fast (edit markdown → run) and slow (edit frontmatter → compile →
  commit both files → run). The ability to edit the markdown body directly
  on GitHub.com is especially useful for on-the-fly instruction adjustments
  without a local development environment. For Ch01 (Daily Workflows): this
  boundary is practical guidance for teams managing workflows — day-to-day
  instruction tuning is fast; structural changes require the compile toolchain.

### Claim 6: Best practice naming convention is descriptive kebab-case (e.g., `issue-responder.md`, `weekly-summary.md`); both source and lock files must be committed to the repository

- **Evidence**: The page lists five best practices: "Use descriptive names:
  `issue-responder.md`, `pr-reviewer.md`"; "Follow kebab-case convention:
  `weekly-summary.md`"; "Avoid spaces and special characters"; "Commit source
  files: Always commit `.md` files"; "Commit generated files: Also commit
  `.lock.yml` files for transparency."
- **Confidence**: settled (first-party; explicit recommendations from the
  reference page)
- **Quote**: "Commit generated files: Also commit `.lock.yml` files for
  transparency"
- **Our assessment**: The naming convention guidance (kebab-case, descriptive)
  mirrors standard GitHub Actions workflow naming conventions, making agentic
  workflows visually consistent with existing CI/CD workflows in `.github/workflows/`.
  The requirement to commit both `.md` and `.lock.yml` is significant: it means
  the compiled artifact (with its embedded security hardening, action SHA pins,
  and metadata header) is part of the repository's version-controlled state,
  not a transient build output. Transparency is the stated reason — reviewers
  can see exactly what will execute (`.lock.yml`) alongside the source
  (`.md`) in the same PR diff. For Ch02: add "commit both source and lock
  files" to the harness engineering checklist. A PR that changes only `.md`
  without a corresponding `.lock.yml` update (when frontmatter changed) is
  a workflow drift risk.

## Concrete Artifacts

### Canonical Minimal Workflow Example

```yaml
---
on:
  issues:
    types: [opened]
tools:
  github:
    toolsets: [issues]
---
# Workflow Description
Read the issue #${{ github.event.issue.number }}. Add a comment to the issue listing useful resources and links.
```

*Source: `reference/workflow-structure` — Core Components section. Verbatim
example as shown on the page. Demonstrates the minimal two-component structure:
YAML frontmatter (trigger on issue opened, GitHub issues toolset) and a
markdown body (single instruction sentence with template variable).*

### File Organization Convention

```
.github/
└── workflows/
    ├── ci-doctor.md          # Source agentic workflow
    └── ci-doctor.lock.yml    # Compiled GitHub Actions Workflow
```

*Source: `reference/workflow-structure` — File Organization section.*

### Lock File Metadata Header Format

```
# gh-aw-metadata: {"schema_version":"v3","frontmatter_hash":"...","strict":true,"agent_id":"copilot"}
```

Field meanings:
- `schema_version`: Lock file schema version (currently "v3"); enables forward-compatible tooling
- `frontmatter_hash`: Hash of the compiled frontmatter YAML; used to detect
  drift between `.md` source and `.lock.yml` (if hash doesn't match current
  frontmatter, recompile is needed)
- `strict`: Whether compiled with `--strict` validation (`true`/`false`)
- `agent_id`: Configured AI engine identity at compile time (e.g., `"copilot"`,
  `"claude"`) — embedded for auditability and reproducibility

*Source: `reference/workflow-structure` — Lock File Structure section.
Verbatim header line as documented on the page.*

### Naming and File Commitment Best Practices

```
Naming convention:
  ✓ issue-responder.md    (descriptive, kebab-case)
  ✓ pr-reviewer.md        (descriptive, kebab-case)
  ✓ weekly-summary.md     (descriptive, kebab-case)
  ✗ Issue Responder.md    (spaces — avoid)
  ✗ issueresponder.md     (not kebab-case)

File commitment:
  ✓ Always commit source (.md) files
  ✓ Always commit generated (.lock.yml) files — for transparency and auditability
  ✗ Treating .lock.yml as a transient build artifact (do not gitignore it)
```

*Source: `reference/workflow-structure` — Best Practices section.*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-how-they-work.md` Claim 1 (YAML frontmatter + markdown two-
    component structure enables sandboxed agentic programming): this reference
    page provides the concrete structural specification — the actual file format
    and directory convention — that Claim 1 describes at a conceptual level.
    Together they give both the "why" (Claim 1) and the "what does it look like"
    (this source).
  - `docs-ghaw-how-they-work.md` Claim 7 (`.md` → `.lock.yml` compilation model):
    this page's Claim 3 and Claim 2 are the structural reference for that model.
    The pairing convention (`ci-doctor.md` → `ci-doctor.lock.yml`) and the
    `.github/workflows/` directory location are authoritative here.
  - `docs-ghaw-compilation-process.md` Claim 7 (only frontmatter changes require
    recompilation; markdown body loaded at runtime): this page's Claim 5 is the
    authoritative statement of that property, directly quoted from the structural
    reference. `docs-ghaw-compilation-process.md` explains the technical mechanism;
    this page states the user-facing rule.
  - `blog-ghaw-weekly-2026-03-23.md` Claim 7 (lock files embed agent ID/model,
    gh-aw-metadata v3): this page's Claim 4 provides the verbatim format of the
    `gh-aw-metadata` header that Claim 7 in that weekly update describes as a
    new capability. The header format (`schema_version`, `frontmatter_hash`,
    `strict`, `agent_id`) is documented here in the reference page.

- **Extends**:
  - `docs-ghaw-how-they-work.md` Claim 11 (compile → watch → run → review
    development workflow): Claim 5 here (markdown editable without recompile)
    adds precision to that workflow — specifically, "watch and run" apply to
    markdown-only changes without compile; compile is only required for
    frontmatter changes. The development loop has two sub-loops: fast
    (markdown-only) and slow (frontmatter + compile).
  - `docs-ghaw-frontmatter-full-reference.md` Claim 1 (frontmatter is generated
    from JSON Schema — the machine-readable contract): this structural reference
    page establishes the physical context for that frontmatter — where it lives
    in the file (between `---` markers), where the file lives on disk
    (`.github/workflows/`), and how it is compiled into a lock file. The
    frontmatter-full reference covers *what fields exist*; this page covers
    *where the frontmatter goes* and *what the compiled output looks like*.
  - `docs-ghaw-compilation-process.md` Claim 6 (action pinning to SHAs and
    `actions-lock.json`): the lock file header's `frontmatter_hash` field
    (Claim 4 here) complements the SHA pinning coverage there. Together they
    explain what the lock file captures: action SHAs (supply-chain integrity),
    frontmatter hash (drift detection), and agent identity (model provenance).

- **Contradicts**: None. All claims on this reference page are consistent with
  the existing corpus. The two-component model, compilation model, editability
  boundary, and naming conventions are corroborated by multiple existing notes.
  No contradiction issue required.

- **Novel**:
  - **Lock file metadata header format** (Claim 4): The verbatim `gh-aw-metadata`
    header with its four fields (`schema_version`, `frontmatter_hash`, `strict`,
    `agent_id`) is documented nowhere else in the corpus. `blog-ghaw-weekly-
    2026-03-23.md` Claim 7 mentions that lock files embed agent ID/model, but
    the complete header format — including `frontmatter_hash` and `strict` — is
    novel to this source.
  - **Frontmatter hash as drift detection mechanism** (Claim 4): No existing
    note documents how the platform detects whether a `.lock.yml` is current
    with its `.md` source. The `frontmatter_hash` field in the metadata header
    is the mechanism, and it is novel to this source.
  - **File naming conventions** (Claim 6): The specific kebab-case convention
    with examples (`issue-responder.md`, `pr-reviewer.md`, `weekly-summary.md`)
    and the explicit "commit both files" requirement are not documented in any
    other source note.
  - **Canonical minimal workflow example** (Concrete Artifacts): The verbatim
    minimal example — two frontmatter fields (`on.issues.types`, `tools.github.
    toolsets`) and a single-sentence markdown body — is a concrete reference
    artifact not present in other notes. `docs-ghaw-how-they-work.md` describes
    the structure; this page shows the simplest working form.

## Guide Impact

### Chapter 01: Daily Workflows

- **Add editability model to workflow iteration guidance** (Claim 5): The guide
  should distinguish two iteration loops: (1) fast loop — edit markdown body,
  re-run, no compile; (2) slow loop — edit frontmatter, compile, commit both
  files, re-run. This distinction directly affects how quickly practitioners
  can tune agent behavior day-to-day. Instruction tuning (the fast loop) has
  zero toolchain friction; structural changes (the slow loop) require a local
  `gh aw` install and a compile step.

### Chapter 02: Harness Engineering

- **Add file organization convention as foundational reference** (Claims 2, 6):
  The guide should document that gh-aw workflows live in `.github/workflows/`
  as `.md` files with paired `.lock.yml` outputs. The kebab-case naming convention
  and the requirement to commit both files should be presented as harness
  engineering hygiene rules — analogous to committing `package-lock.json` in
  Node.js projects. A PR that changes `.md` frontmatter without updating
  `.lock.yml` is a workflow drift risk.

- **Add minimal workflow example as a starting template** (Concrete Artifacts):
  The canonical minimal example (trigger on issue opened, GitHub issues toolset,
  single-sentence instruction) is a useful starting point for Ch02 examples.
  It demonstrates the minimum viable structure and can be built up incrementally.

- **Add `gh-aw-metadata` header as a lock file reference** (Claim 4): Document
  the header format and the meaning of each field. Specifically, explain
  `frontmatter_hash` as the drift detection mechanism — if a reviewer sees a
  lock file with a mismatched hash, the workflow needs recompilation. This is
  practical debugging guidance for teams working with multiple workflow files.

### Chapter 03: Safety and Verification

- **Add `agent_id` in lock files to the auditability section** (Claim 4): The
  `agent_id` field embedded in the `gh-aw-metadata` header captures which AI
  engine was configured at compile time. This is relevant to Ch03's audit and
  verification discussion: compiled lock files are not just executable artifacts,
  they are provenance records that capture the intended model. Pair with
  `blog-ghaw-weekly-2026-03-23.md` Claim 7 for the full picture of what lock
  files record for auditability.

## Extraction Notes

1. **Relatively focused reference page**: Unlike the frontmatter full reference
   or the compilation process reference, this page is concise and structural.
   The WebFetch returns appeared complete — the page covers a single focused
   topic (what a workflow file looks like) rather than an exhaustive field catalog.
   Three fetches with different prompts were used to maximize quote accuracy.

2. **Quote accuracy**: Direct quotes are used only where WebFetch returned
   consistent text across multiple fetches. The lock file metadata header
   (`# gh-aw-metadata: ...`) is likely verbatim from the page. The editability
   model quote ("The markdown body is loaded at runtime and can be edited
   directly on GitHub.com without recompilation. Only frontmatter changes require
   recompilation.") is consistent across two fetches and assessed as
   near-verbatim. The best practices are paraphrased from the page's bulleted
   list; specific name examples (`issue-responder.md`) are likely verbatim.

3. **No publication date**: The page carries no explicit publication date.
   `date_published` is left null. The lock file metadata `schema_version: v3`
   is consistent with gh-aw v0.62.x+ (the version that introduced gh-aw-metadata
   v3, per `blog-ghaw-weekly-2026-03-23.md`).

4. **Previous mining attempt**: PR #688 was previously opened for this issue
   and subsequently closed. The current note is a new extraction from the same
   source. This note adds the `frontmatter_hash` drift detection interpretation
   and provides more complete cross-references to `docs-ghaw-compilation-process.md`
   (filed after the previous attempt) and `docs-ghaw-frontmatter-full-reference.md`.

5. **No contradictions filed**: All claims are consistent with the existing
   corpus. The two-component model, compile/runtime boundary, and lock file
   structure are corroborated by multiple existing notes.
