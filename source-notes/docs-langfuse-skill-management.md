---
source_url: https://langfuse.com/docs/skill-management/overview
source_type: docs
title: "Skill Management — Langfuse"
author: Langfuse (Langfuse GmbH / Finto Technologies Inc.)
date_published: "2026-11-03 (changelog image date; page itself undated)"
date_extracted: 2026-11-04
last_checked: 2026-11-04
status: current
confidence_overall: settled
issue: "#2014"
---

# Skill Management — Langfuse

> Langfuse's skill-management feature treats an agent skill folder as a
> versioned deployment artifact: publish `SKILL.md` plus supporting files,
> promote or roll back with mutable labels, fetch by label/version, and
> explicitly instrument available skills and loaded files because the registry
> does not trace skill usage on its own. The page also documents a hard,
> text-only packaging envelope that constrains runbook-to-skill conversion.

## Source Context

- **Type**: docs (vendor product documentation — feature overview)
- **Author credibility**: Langfuse is a production LLM-observability/evaluation
  vendor documenting its own shipped feature. Claims about the storage model,
  label resolution, limits, CLI/API behavior, and tracing metadata are
  authoritative descriptions of the product surface (settled). The page makes
  no measured effectiveness claims. The UI path is explicitly gated behind
  Feature Preview, so mechanics are documented-but-preview rather than a
  long-stable contract.
- **Scope**: The overview, plus four linked pages followed per MINER.md §1:
  skill version control (`/docs/skill-management/version-control`), get started
  (`/docs/skill-management/get-started`), trace linking
  (`/docs/skill-management/tracing`), and the prompt/skill concepts page
  (`/docs/prompt-and-skill-management/concepts`). Covers publishing,
  versioning/labels, loading, tracing, limits, and the upstream Agent Skills
  format comparison. Does NOT cover prompt management in depth (sibling note
  #319) or the Langfuse Agent Skill itself (sibling note #1056), and does not
  document protected labels for skills.

## Extracted Claims

### Claim 1: A Langfuse skill is a multi-file instruction set — a required root `SKILL.md` plus optional supporting files — that is stored and versioned as one artifact
- **Evidence**: The overview's opening definition; the concepts page's
  "Skill structure" section; the limits table's "Files per version" row.
- **Confidence**: settled
- **Quote**: "A skill is an instruction set to your agent. Similar to a prompt, but it can contain multiple files and more complex patterns."
- **Our assessment**: This is the artifact-class definition: prompts are single
  files, skills are folders. The distinction matters operationally because a
  skill version has a file manifest, not just a string. The page points to the
  open Agent Skills format for the deeper structure; the concepts page adds
  that `name` and `description` are required frontmatter fields and that
  additional frontmatter is preserved but interpreted by the agent framework.

### Claim 2: Every version is a complete snapshot of the whole skill; changing any one file creates a new version of the entire file set
- **Evidence**: The overview says each version saves the complete set of files;
  the concepts page spells out the consequence for a multi-file skill.
- **Confidence**: settled
- **Quote**: "A version is always scoped to the entire prompt or skill object. This means that if one file in a skill changes, the entire skill (all its files) gets a new version."
- **Our assessment**: This is the key unit-of-change rule. There is no
  per-file versioning or partial update: a one-line edit to a reference file
  produces a new full-skill version. That is simple for rollback (one version
  number maps to one coherent file set) but means storage/diff review is
  whole-folder, not per-file. The UI supports reviewing file diffs before
  publishing, but the version boundary remains the skill.

### Claim 3: Labels are mutable pointers that promote or roll back a version without changing application code; publishing a new version does not move `production`
- **Evidence**: The overview's publish/version section; the version-control
  page's rollback workflow; the concepts page's deployment workflow.
- **Confidence**: settled
- **Quote**: "Move `production` to the version you want agents to fetch. Move it to an earlier version to roll back. Requests pinned to an exact version are unaffected."
- **Our assessment**: This is the load-bearing ops claim — the skill analogue
  of prompt versioning (#319 Claim 4). A deployment is a label move, not a
  code deploy or container restart. The version-control page is explicit that
  publishing v2 leaves `production` on v1 until the label is moved, so
  published and production-served are separate states. The label PATCH
  replaces the version's user-managed labels, so callers must include every
  label the version should retain; `latest` is managed automatically.

### Claim 4: Label resolution is fail-closed — no label serves `production`, a missing label returns 404 rather than falling back, and label+version together is a 400
- **Evidence**: The version-control page's label-resolution table and its
  explanation of the no-fallback rule.
- **Confidence**: settled
- **Quote**: "If no version carries the requested label, the request fails with `404 Not Found`. Langfuse never silently falls back to `production` or `latest`"
- **Our assessment**: This is a good reliability property and the opposite of
  a common feature-flag footgun. A typo or never-assigned environment label
  surfaces immediately as a failed fetch instead of silently serving the wrong
  skill. The exact resolution rules are: neither → `production`; `label=` →
  that label or 404; `version=` → that version regardless of labels; both →
  400. Operationally, this makes label names part of the deployment contract.

### Claim 5: Publishing works from UI, CLI folder push, and API file upload; the API payload is the complete desired file set, so omitted files are deleted from the new version while older versions remain unchanged
- **Evidence**: The overview's three publish surfaces; the version-control
  page's UI steps, CLI push, and `POST /api/public/skills` example.
- **Confidence**: settled
- **Quote**: "Send every file the new version should contain to `POST /api/public/skills`. Omitting a file removes it from the new version; earlier versions stay unchanged."
- **Our assessment**: The API is declarative: the request is the full desired
  state, not a patch. That is a sharp operational edge — an incomplete upload
  silently drops files from the new version. The CLI is friendlier because it
  pushes a local folder and only creates a version if the files differ from the
  latest saved version. Importing existing skills is also non-destructive to
  production: the page says importing leaves existing `production` labels
  unchanged.

### Claim 6: Langfuse is the registry, not the runtime — the agent framework makes skills available to the model and controls file loading and script execution, and installation alone does not make the model use a skill
- **Evidence**: The overview's load section; the get-started page's CLI install
  caveat; the concepts page's progressive-loading description.
- **Confidence**: settled
- **Quote**: "Your agent framework makes skills available to the model and controls file loading and script execution."
- **Our assessment**: This boundary is the most important scoping claim for
  the guide. Langfuse stores and distributes the artifact; it does not inject
  instructions into the model or run scripts. "Installation alone does not make
  the model use the skill" is the operational consequence: installing files is
  preparation, not activation. Any reliability claim about skill execution must
  therefore be evaluated at the agent-framework layer, not the registry layer.

### Claim 7: The packaging envelope is hard and specific — 200 files, 1,000,000 UTF-8 bytes, relative POSIX paths ≤512 chars, text-only extensions, name 1–64 chars, description 1–1024 chars, ≤50 tags, ZIP ≤3 MiB, content fetch 1–50 hashes / ≤10 MB
- **Evidence**: The overview's "Current limits" table, reproduced verbatim in
  Concrete Artifacts below.
- **Confidence**: settled
- **Quote**: "Relative POSIX paths, up to 512 characters; no duplicates, absolute paths, backslashes, or `.` / `..` segments"
- **Our assessment**: These are concrete registry constraints, not style
  guidance. They directly bound what can be converted into a managed skill: a
  runbook folder with a large asset bundle, absolute paths, symlinks, binary
  PDFs, or more than 200 files will not import as-is. The 1 MB total-content
  limit is especially relevant for reference-heavy skills: it constrains how
  much operational documentation can ship in one version before it must be
  split or linked rather than embedded. The ZIP cap applies before extraction,
  and imported files still must satisfy the per-version limits.

### Claim 8: Langfuse accepts supported text files only, while the open Agent Skills format allows additional file types including binary assets — a concrete compatibility gap
- **Evidence**: The limits table's file-types row and the explicit note directly
  below the table.
- **Confidence**: settled
- **Quote**: "Langfuse currently accepts supported text files only."
- **Our assessment**: The page names the delta rather than hiding it: the
  upstream format permits binary assets, but Langfuse does not. The allowlist
  is broad for source/config/docs files (`.md`, `.txt`, `.json`, `.yaml`,
  `.py`, `.sh`, etc.) and explicitly rejects binary and extensionless files.
  For the guide, this means a skill that depends on images, compiled artifacts,
  or other binary support files cannot be fully represented in this registry.
  It also means scripts are stored as text and executed only if the agent
  framework chooses to run them.

### Claim 9: Publishing or installing does not trace skill usage automatically; operators must report available skills and instrument file-loading tools as separate steps
- **Evidence**: The overview's tracing section and the dedicated tracing page's
  opening and availability caveats.
- **Confidence**: settled
- **Quote**: "Publishing or installing a skill does not trace its usage automatically."
- **Our assessment**: This is the most SRE-relevant claim on the page. Without
  explicit instrumentation, an operator can see that a skill version exists but
  cannot tell which version a model could use or which files an agent actually
  loaded. The tracing page reinforces that installing or fetching skills alone
  records neither the available-skill list nor the loaded-file list. This is a
  registry-to-observability gap that must be closed by the agent, not assumed
  from the registry.

### Claim 10: Available-skill metadata is reported by the agent, not injected by Langfuse; the available list must also be attached to the skill-loading tool observation so Langfuse can resolve the loaded version
- **Evidence**: The tracing page's definitions of available skills and
  loaded skill, plus the OpenTelemetry attribute example.
- **Confidence**: settled
- **Quote**: "Report the same skills your agent can use; Langfuse does not expose them to the model."
- **Our assessment**: This separates two things operators often conflate:
  Langfuse records what the agent says is available, but it does not make the
  skill available. The loaded-skill link requires the available list on both
  the generation and the tool observation. That produces a useful trace model
  (requested vs loaded files), but its correctness depends on the agent
  reporting truthfully. The usage tab then aggregates available and loaded
  observation counts, loads per file, and linked observations.

### Claim 11: Skill-load detection is a documented tool-name/input contract — `loadSkill`/`skill`/`Skill`, `skill_read`, or `readFile`/`Read` — and only counts on a successful, non-null tool result whose input matches an available skill
- **Evidence**: The tracing page's "Instrument skill-loading tools" table and
  its success criteria.
- **Confidence**: settled
- **Quote**: "Langfuse records a skill load when the tool succeeds, returns a non-null output, and its input matches a skill in the available list."
- **Our assessment**: This is a practical observability constraint: custom
  loaders need one of the recognized names/shapes, or the vendor asks for a
  GitHub issue to add support. For `readFile`/`Read`, the path must contain the
  skill name as a directory segment such as
  `.agents/skills/skill_name/SKILL.md`. The contract is stronger than "file was
  read" but weaker than proof the model followed the instructions — it is
  attribution of a successful load, not evidence of skill effectiveness.

### Claim 12: CLI installs land in `.agents/skills/<skill_name>/` and carry a `langfuse-skills.lock`; `install` restores locked versions, `update` follows saved labels, and exact version pins stay fixed
- **Evidence**: The get-started page's CLI install, restore/update, and lockfile
  sections.
- **Confidence**: settled
- **Quote**: "`install` without arguments restores locked versions. `update` updates already locked skills to the versions assigned to their saved labels; exact version pins stay fixed."
- **Our assessment**: The lockfile is the reproducibility control for CLI
  consumers: it records resolved versions so an install can be replayed. It
  also clarifies the two update modes — label-following (`update`) versus
  pinned (`--version`) — which behave differently during a rollback. Discovery
  for tracing reads the same lockfile; folders without lockfile entries have
  no version, so an untracked local skill cannot be linked to a registry
  version.

### Claim 13: Label moves propagate differently by consumer — API clients pick up the change on the next manifest request (refresh app caches), while CLI installations keep old files until `langfuse skills update`, and version pins never move
- **Evidence**: The version-control page's rollback and label-move notes; the
  get-started page's manifest and fixed-version guidance.
- **Confidence**: settled
- **Quote**: "For CLI installations, moving a label does not change installed files until you run `langfuse skills update`. An exact version pin remains fixed."
- **Our assessment**: This is the rollback-propagation caveat that operators
  must design for. A label flip is not an instantaneous fleet-wide update:
  API-fetching agents see it on their next manifest request after cache
  refresh, while disk-installed CLI agents need an explicit update command.
  Pinned agents are intentionally unaffected — useful for canaries, dangerous
  if used unintentionally in production. The page also warns to keep the
  resolved version fixed during a run so instructions and supporting files come
  from the same revision.

### Claim 14: Fetching supports manifests and content hashes, so agents can resolve a version, fetch only needed files, and cache by hash instead of downloading the whole skill on every request
- **Evidence**: The get-started page's "Fetch files on demand" section and the
  concepts page's manifest description.
- **Confidence**: settled
- **Quote**: "Cache content by hash to reuse it across requests."
- **Our assessment**: The manifest-plus-hash design is a sensible distribution
  mechanism for progressive disclosure: the agent reads metadata, then fetches
  only the `SKILL.md` or reference files it needs. The 1–50 hashes and 10 MB
  per-request cap (Claim 7) bound the batch size. Content-addressed caching is
  the operational optimization; the version pin is the correctness control.

### Claim 15: Skill Management is a Feature Preview capability, enabled through account-menu preview toggles (V4 Preview first, then Skill Management) before the Skills UI is visible
- **Evidence**: The get-started page's UI creation steps.
- **Confidence**: settled
- **Quote**: "If **Skills** is not visible, enable **Skill Management** under **account menu → Feature Preview**. Enable **V4 Preview** first if its toggle is disabled."
- **Our assessment**: The preview gate is the strongest signal that this is not
  yet a long-stable production contract. The Prospector also characterized the
  feature as beta. The mechanics above are documented and inspectable, but the
  guide should frame the pattern as an emerging vendor implementation rather
  than an industry-standard capability. There is no practitioner evidence on
  the page for skill-versioning effectiveness or incident reduction.

## Concrete Artifacts

### Current limits table (verbatim, `langfuse.com/docs/skill-management/overview`)

| Resource | Limit or requirement |
| --- | --- |
| Files per version | Up to 200, including the root `SKILL.md` |
| Total file content per version | Up to 1,000,000 UTF-8 bytes |
| File paths | Relative POSIX paths, up to 512 characters; no duplicates, absolute paths, backslashes, or `.` / `..` segments |
| File types | Supported text extensions, including `.md`, `.txt`, `.json`, `.yaml`, `.py`, and `.sh`; binary and extensionless files are unsupported |
| Skill name | 1–64 characters: lowercase letters, digits, and single hyphens; no leading, trailing, or consecutive hyphens |
| Description | 1–1024 characters |
| Tags | Up to 50 per skill, 1–100 characters each |
| Local ZIP import | Up to 3 MiB (3,145,728 bytes) per ZIP before extraction; imported skill files must fit the limits above |
| Content fetch | 1–50 content hashes and up to 10,000,000 UTF-8 bytes of combined content per request |

### Supported file extensions (verbatim, `langfuse.com/docs/skill-management/overview`)
```
.md .markdown .mdx .txt .rst .adoc .json .jsonc .jsonl .ndjson
.yaml .yml .toml .xml .csv .tsv .ini .cfg .conf .properties
.log .html .htm .css .scss .sass .less .js .jsx .mjs
.cjs .ts .tsx .py .pyi .sh .bash .zsh .fish .ps1
.rb .go .rs .java .c .h .cc .cpp .hpp .cs
.swift .kt .kts .lua .r .pl .php .sql .graphql .gql
.tex
```

### Label resolution table (verbatim, `langfuse.com/docs/skill-management/version-control`)
| You pass | Langfuse returns |
| --- | --- |
| Neither `label` nor `version` | The version labeled `production`. If no version has that label, the request fails with `404`. |
| `label="staging"` | The version that currently carries `staging`. If no version does, `404` — there is no fallback to `production` or `latest`. |
| `version=3` | Version 3, regardless of its labels. |
| Both `label` and `version` | A `400` error: the two are mutually exclusive. |

### Publish a local folder and assign a label (verbatim CLI, get-started / version-control)
```bash
langfuse skills push ./skill_name --label staging
langfuse skills push ./skill_name --label production
```

### Publish via API (verbatim, version-control)
```bash
curl --request POST "$LANGFUSE_BASE_URL/api/public/skills" \
  --user "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  --header "Content-Type: application/json" \
  --data '{
    "files": [{
      "path": "SKILL.md",
      "content": "---\nname: skill_name\ndescription: Describe when to use this skill.\n---\nInstructions for the agent."
    }],
    "commitMessage": "Update skill instructions"
  }'
```

### Promote a version to production (verbatim, version-control)
```bash
curl --request PATCH \
  "$LANGFUSE_BASE_URL/api/public/skills/skill_name/versions/2" \
  --user "$LANGFUSE_PUBLIC_KEY:$LANGFUSE_SECRET_KEY" \
  --header "Content-Type: application/json" \
  --data '{"labels":["production"]}'
```

### Install, pin, restore, and update (verbatim CLI, get-started / version-control)
```bash
langfuse skills install skill_name --label production
langfuse skills install skill_name --version 2
langfuse skills install --tag tag
langfuse skills install
langfuse skills update
```

### Report available skills on an OTel span (verbatim, tracing page)
```json
{
  "langfuse.observation.skills_available": "[{\"name\":\"skill_name\",\"version\":2}]"
}
```

### Recognized skill-loading tools (verbatim table, tracing page)
| Tool | Input identifying the resource |
| --- | --- |
| `loadSkill`, `skill`, `Skill` | Skill name in `name` or `skill`; resolves the root `SKILL.md` |
| `skill_read` | `skillName` and a relative `path` |
| `readFile`, `Read` | Installed file path in `path` or `file_path` |

## Cross-References

- **Corroborates**:
  - `docs-langfuse-prompt-management.md` (#319) **Claim 4** — prompt versions
    are immutable numeric history while labels are mutable pointers to
    versions, and code references labels rather than versions. This note
    applies the same model to skills (Claims 2–4), with the additional
    multi-file snapshot semantics.
  - `docs-langfuse-prompt-management.md` (#319) **Claim 5** — the five-step
    prompt deployment lifecycle Create → Validate → Deploy → Monitor →
    Rollback. This note's label promotion/rollback (Claims 3, 13) is the
    skill-side instance of the same deploy-gate pattern.
  - `docs-langfuse-agent-skill.md` (#1056) **Claim 3** (the Agent Skill is a
    self-contained folder with a `SKILL.md` entrypoint plus reference docs) and
    **Claim 4** (progressive disclosure: frontmatter always loaded, full
    instructions and references on demand). This note is about the *managed
    registry* for user-authored skills, not the skill Langfuse ships, but the
    packaging and disclosure model are the same.
  - `blog-anthropic-agent-skills.md` (#608) **Claim 2** (a skill is a directory
    with a `SKILL.md` carrying required `name`/`description` frontmatter),
    **Claims 3–4** (progressive disclosure through metadata, body, and linked
    files), and **Claim 5** (skills can include code/scripts). Langfuse
    implements those format mechanics (Claims 1, 6, 14) but constrains the file
    types (Claim 8).
  - `docs-langfuse-glossary.md` (#255) **Claim 8** — Prompt Management stores,
  versions, and retrieves prompts so updates are decoupled from code
  deployment, with labels such as `production`/`staging`. This note extends
  that same concern from prompt strings to multi-file skills.

- **Contradicts**: None. The text-only limitation (Claim 8) is a documented
  subset of the upstream Agent Skills format, not a contradiction of #608 or a
  claim that Langfuse supports binary assets. No contradiction issue filed.

- **Extends**:
  - `docs-langfuse-roadmap.md` (#320) **Claim 4** — the roadmap listed
    "skill management" as a planned CLI/MCP/skill improvement. This note
    documents the shipped (Feature Preview) realization, upgrading the
    corpus's status from planned to existing.
  - `docs-langfuse-cli.md` (#1057) **Claim 2** — the CLI wraps the full
    OpenAPI surface, so every API endpoint is a CLI command. This note adds the
    skill-specific `skills push/install/update` commands and the
    `langfuse-skills.lock` install contract (Claim 12), which the earlier CLI
    note could not cover.
  - `docs-langfuse-sdk-overview.md` (#302) **Claim 10** — `propagate_attributes`
    distributes user/session/metadata/version/tags/environment to child
    observations. The tracing page extends that propagation model with a
    skills-available attribute (`langfuse.observation.skills_available`) and
    its Python/JS helpers (Claim 10 here).
  - `docs-promptfoo-test-agent-skills.md` (#1799) **Claim 1** (a skill version
    is evalable by swapping only `SKILL.md`) and **Claim 4** (the
    `skill-used` signal has different evidentiary strength per provider —
    first-class tool call vs inferred file read). This note's tracing contract
    (Claims 9–11) is the registry-side complement: Langfuse records which
    version was available and which successful load tool fired, while promptfoo
    supplies the eval-time attribution and boundary tests. Neither closes the
    gap alone.

- **Novel** (first appearances in the corpus):
  - A **managed skill registry** with whole-folder version snapshots and
    mutable environment labels (Claims 2–5) — the corpus had skill *packaging*
    (#1056, #608) and prompt versioning (#319), but not a registry for
    user-authored multi-file skills.
  - The **concrete packaging envelope** for a skill registry (Claim 7) and the
    explicit **text-only vs upstream binary support gap** (Claim 8).
  - The **registry-to-tracing gap** (Claims 9–11): publishing/installing is not
    usage telemetry, available-skill metadata is agent-reported, and load
    detection depends on a documented tool-name contract.
  - The **lockfile-based reproducibility model** for CLI-installed skills and
    the consumer-specific rollback propagation semantics (Claims 12–13).
  - **Manifest + content-hash fetching** for progressive skill loading
    (Claim 14).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability)**: Add the managed-skill lifecycle as the
  multi-file analogue of prompt versioning: whole-folder immutable versions,
  mutable `staging`/`production` labels, promotion/rollback by label move
  rather than code deploy, and the propagation caveats (Claim 13). The
  fail-closed label resolution (Claim 4) and the lockfile-install model
  (Claim 12) are concrete reliability practices the chapter can recommend:
  make label names a deployment contract, and distinguish label-following
  installs from exact version pins. Cite Claims 2–5, 12–13.

- **Chapter 02 (Observability)**: Add a specific "skill usage is not traced by
  default" warning (Claim 9). Recommend reporting available skill
  names/versions on model-call spans and attaching the same list to
  skill-loading tool observations (Claims 10–11), then using the per-skill
  Usage tab (available vs loaded counts, loads per file) to verify which
  versions were reachable and which files were actually read. Pair this with
  #1799's eval-side `skill-used` attribution to show that trace-time load
  evidence and eval-time routing evidence are different controls.

- **Chapter 03 (Runbooks and Agents)**: Use skill management as the worked
  example of turning runbooks into versioned agent artifacts — but call out the
  packaging envelope as a conversion constraint (Claim 7): 200 files, 1 MB
  total text, ≤512-char relative POSIX paths, text-only extensions, 3 MiB ZIP
  imports. A runbook with binary assets or hundreds of files cannot be
  imported unchanged. Also record the registry/runtime boundary (Claim 6):
  Langfuse does not make the model use a skill or execute scripts; the agent
  framework owns loading and execution, so runbook reliability must be
  evaluated at the framework layer.

- **Chapter 06 (Security and Trust)**: Note that the registry stores `.py`,
  `.sh`, and other text-based scripts but the registry is not the executor
  (Claims 6, 8). The text-only allowlist reduces the artifact surface compared
  with a binary-capable format, but it does not remove the need for the
  trust-at-install and file-audit controls in #608 Claim 10, because scripts
  are still text files that an agent framework may run. The Feature Preview
  status (Claim 15) means the control set may change.

## Extraction Notes

- Source fetched 2026-11-04 via WebFetch (Markdown rendering). The overview
  page is short, so per MINER.md §1 four substantive linked pages were
  followed: version control, get started, tracing, and the shared
  prompt/skill concepts page. The linked `agentskills.io` spec was not fetched;
  the Langfuse pages state the relevant compatibility delta directly and the
  corpus already covers the open standard (#608).
- Quotes are copied verbatim from the fetched Markdown. The limits table,
  label-resolution table, tool-recognition table, and shell/JSON examples in
  Concrete Artifacts are reproduced from the source pages; the table
  formatting is normalized to Markdown but cell text is unchanged. The
  supported-extension block is reproduced exactly.
- `date_published` is recorded as 2026-11-03 from the changelog screenshot
  filenames (`2026-11-03-skill-management-*.png`); the page itself does not
  expose a publication date. `last_checked` and `date_extracted` are
  extraction-day UTC.
- `confidence_overall: settled` reflects that the claims describe a shipped,
  inspectable vendor feature (storage, label resolution, limits, CLI/API,
  tracing attributes) rather than effectiveness. It does not assert that
  skill versioning improves reliability. Per the Prospector's note, the feature
  is beta/Feature Preview and vendor-documented with no practitioner evidence;
  Claim 15 records that caveat and the Guide Impact sections frame the pattern
  as emerging practice.
- miner-related-notes.md candidates processed (cite or dismiss each):
  - `docs-langfuse-security-and-guardrails.md` — **Dismissed**. Guardrail
    scanner pipeline and security scores; no skill registry, versioning, or
    packaging claims.
  - `docs-langfuse-mcp-server.md` — **Dismissed**. Docs/data-platform MCP
    server surface; skill distribution here is CLI/SDK/REST, not MCP.
  - `docs-langfuse-agent-skill.md` — **Cited** (Corroborates Claims 3–4:
    packaging and progressive disclosure; distinguished as the vendor's own
    skill, not the registry).
  - `docs-langfuse-roadmap.md` — **Cited** (Extends Claim 4: planned skill
    management is now shipped in Feature Preview).
  - `docs-langfuse-sdk-overview.md` — **Cited** (Extends Claim 10: attribute
    propagation extended to `skills_available`).
  - `docs-litellm-evals-api.md` — **Dismissed**. Evaluation API state and
    graders; no skill artifact or registry overlap.
  - `docs-litellm-batches-api.md` — **Dismissed**. Batch rate limits and
    token accounting; no skill distribution overlap.
  - `docs-litellm-bedrock-invoke.md` — **Dismissed**. Bedrock passthrough
    routing/auth; unrelated surface.
  - `docs-promptfoo-evaluate-coding-agents.md` — **Dismissed**. Coding-agent
    eval tiers and workspace isolation; workspace/agent evaluation, not skill
    registry versioning.
  - `docs-langfuse-glossary.md` — **Cited** (Corroborates Claim 8:
    prompt-management version/label definition, extended here to skills).
- Additional manual search of `source-notes/`: `docs-langfuse-prompt-management.md`
  (#319) **Cited** (Claims 4–5). `docs-langfuse-cli.md` (#1057) **Cited**
  (Claim 2). `blog-anthropic-agent-skills.md` (#608) **Cited** (Claims 2–5).
  `docs-promptfoo-test-agent-skills.md` (#1799) **Cited** (Claims 1, 4).
- No contradiction issue filed: no claim materially opposes an existing note.
  The text-only restriction is an explicit subset of the upstream format, not
  an opposing claim.
