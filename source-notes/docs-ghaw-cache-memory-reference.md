---
source_url: https://github.github.com/gh-aw/reference/cache-memory
source_type: docs
title: "GitHub Agentic Workflows: Cache Memory Reference"
author: GitHub Agentic Workflows team (official reference documentation)
date_published: null
date_extracted: 2026-05-24
last_checked: 2026-05-24
status: current
confidence_overall: emerging
issue: "#360"
---

# GitHub Agentic Workflows: Cache Memory Reference

> The formal reference specification for `cache-memory` — fills the technical spec
> gap across the corpus by providing the storage backend (GitHub Actions Cache,
> 10GB/LRU), configuration surface (key, retention-days 1–90, allowed-extensions),
> multiple named caches, integrity-aware isolation, shared-import merge semantics,
> and the troubleshooting error vocabulary (`cache_memory_miss`) that no pattern guide
> documents.

## Source Context

- **Type**: docs (official GitHub Agentic Workflows documentation, `reference/`
  URL section — authoritative technical specification, distinct from the `guides/`
  and `patterns/` sections that use `cache-memory` as a supporting mechanism)
- **Author credibility**: First-party reference documentation from the GitHub Agentic
  Workflows team (GitHub Next / Microsoft Research). Storage backend specs,
  configuration options, and error vocabularies are authoritative for the `gh aw`
  platform. Prior pattern guides (`docs-ghaw-dailyops.md`, `docs-ghaw-expert-ops.md`,
  `docs-ghaw-audit-with-agents.md`) use `cache-memory` from a practitioner perspective;
  this reference page is the authoritative technical specification behind those uses.
- **Scope**: Covers the complete configuration surface for `cache-memory`: basic and
  advanced YAML options (key, retention-days, allowed-extensions), multiple named cache
  configurations, storage backend specifications (GitHub Actions Cache, 10GB limit,
  LRU eviction), cross-branch accessibility, compiler-managed fallback keys,
  integrity-aware isolation, shared workflow merge semantics, automatic cleanup
  behavior, security considerations (including threat detection integration),
  troubleshooting patterns (`cache_memory_miss`), and a formal comparison against
  `repo-memory`. Does NOT cover: `repo-memory` configuration (separate tool), the
  Safe Outputs permission model (see `docs-ghaw-how-they-work.md`), the cleanup
  lifecycle implementation details (see `docs-ghaw-ephemerals.md`), or usage
  patterns from specific workflows.

## Extracted Claims

### Claim 1: Cache Memory's storage backend is GitHub Actions Cache with a 10GB per-repository limit and LRU eviction — the first documented capacity constraint on cross-run agent state in the corpus

- **Evidence**: Listed as a spec bullet under "Behavior and Limitations" with an
  explicit capacity specification and eviction policy. The 10GB limit is a GitHub
  Actions platform constraint, not an arbitrary gh-aw parameter.
- **Confidence**: settled (first-party reference documentation; capacity limit is
  platform-level infrastructure spec)
- **Quote**: "Storage backend: GitHub Actions Cache with 10GB per-repository limit
  and LRU eviction"
- **Our assessment**: The 10GB limit with LRU eviction is architecturally significant
  for long-running ExpertOps or DailyOps workflows that accumulate state over months.
  An agent that appends daily observations without cleanup could approach this limit
  depending on data volume. LRU eviction means the platform self-manages within the
  limit, but teams should still monitor growth. This capacity constraint is why
  `docs-ghaw-ephemerals.md` Claim 6's keep-latest-per-prefix cleanup strategy
  matters — it prevents both the LRU cap from being hit and the per-workflow prefix
  group from accumulating stale entries. For Ch02 (Harness Engineering): add the
  10GB/LRU constraint as the definitive capacity spec for cache-memory.

### Claim 2: Default retention is 7 days; `retention-days` extends access to 1–90 days by uploading artifacts rather than relying solely on cache expiration

- **Evidence**: "Behavior and Limitations" section spec bullet. The "Advanced Options"
  section documents `retention-days: 30` with the range note `# 1-90 days`. The
  mechanism is artifact upload, not cache TTL adjustment.
- **Confidence**: settled (first-party reference documentation; the 1–90 day range
  aligns with GitHub Actions artifact retention constraints)
- **Quote**: "Retention: 7 days default; `retention-days` uploads artifacts for
  extended access (1-90 days)"
- **Our assessment**: The 7-day default is confirmed across multiple sources.
  What is new here is the extension mechanism: `retention-days` triggers artifact
  upload rather than adjusting cache TTL — retention extension and live cache storage
  are decoupled. An agent can read from either the live cache (fast, 7-day) or from
  uploaded artifacts (slower, up to 90 days) for recovery from cache eviction.
  This production resilience detail is not described in any pattern guide. For Ch02:
  document `retention-days` as the mechanism for mission-critical state that cannot
  afford 7-day gaps (e.g., a long-running audit baseline or a security observation
  history spanning multiple weeks).

### Claim 3: The minimal `cache-memory: true` configuration stores files at `/tmp/gh-aw/cache-memory/` using a workflow-scoped cache key; named caches append `-{id}/` to the base path

- **Evidence**: "Basic Configuration" section documents `tools: cache-memory: true`
  and the overview states the default path. "Multiple Cache Configurations" section
  documents the named-cache path convention.
- **Confidence**: settled (first-party documentation; path convention consistent
  with `docs-ghaw-dailyops.md` Claim 6, `docs-ghaw-expert-ops.md` Claim 6,
  and `docs-ghaw-audit-with-agents.md` Claim 5)
- **Quote**: "The system automatically configures cache directories, restore/save
  operations, and fallback keys at `/tmp/gh-aw/cache-memory/` (default) or
  `/tmp/gh-aw/cache-memory-{id}/` (additional caches)."
- **Our assessment**: The path convention is now authoritatively specified:
  `/tmp/gh-aw/cache-memory/` for the default cache, `/tmp/gh-aw/cache-memory-{id}/`
  for named additional caches. This confirms paths used in all prior source notes
  and provides the formal basis for agents to read/write state without path
  guessing. For Ch02: use these exact paths in all cache-memory harness templates.

### Claim 4: Advanced configuration exposes three options — `key`, `retention-days`, and `allowed-extensions` — that control cache identity, retention, and permitted file types respectively

- **Evidence**: "Advanced Options" section documents all three parameters with a YAML
  example. `key` documentation notes "compiler appends `${{ github.run_id }}`
  automatically." `retention-days` range is 1–90. `allowed-extensions` "restricts
  writable file types when specified."
- **Confidence**: settled (first-party reference documentation; all three parameters
  documented with explicit semantics)
- **Quote**: "key: Custom cache identifier (compiler appends `${{ github.run_id }}`
  automatically)"
- **Our assessment**: The three parameters serve different purposes: `key` is for
  scoping (per-workflow, per-user, cross-repo); `retention-days` is for lifecycle
  (when does the state expire); `allowed-extensions` is for security (which file
  types can the agent write). The `allowed-extensions` restriction is notable —
  it enables teams to restrict agent cache writes to specific formats like `.json`
  or `.md`, preventing agents from persisting arbitrary file types to shared storage.
  No prior pattern guide mentions this security feature. For Ch03 (Safety): document
  `allowed-extensions` as a defense-in-depth option for cache-memory in
  security-sensitive workflows.

### Claim 5: Multiple named caches with separate IDs, keys, and retention policies enable workflows to maintain distinct state stores with different lifecycles

- **Evidence**: "Multiple Cache Configurations" section documents an array form under
  `tools: cache-memory:` with `id:`, `key:`, and `retention-days:` fields per entry.
  Each named cache mounts at `/tmp/gh-aw/cache-memory-{id}/`.
- **Confidence**: settled (first-party reference documentation; YAML example is
  specific)
- **Quote**: (no direct prose quote; evidence is in the YAML configuration — see
  Concrete Artifacts)
- **Our assessment**: Multiple named caches enable a workflow to separate state
  concerns with different retention policies — for example, an `id: session` cache
  with a run-specific key for ephemeral session state vs. an `id: logs` cache with
  7-day retention for rolling log storage. No prior source documented the multi-cache
  configuration pattern or the `/tmp/gh-aw/cache-memory-{id}/` naming convention.
  For Ch02: harness templates for complex stateful workflows should show the
  multi-cache pattern as the mechanism for managing state at different lifecycle
  stages within a single workflow.

### Claim 6: The compiler auto-generates restore-key fallback prefixes by stripping `${{ github.run_id }}` from the cache key, enabling progressive cache hits across runs without manual fallback configuration

- **Evidence**: "Fallback mechanism" bullet in "Behavior and Limitations":
  "Compiler generates restore-key prefixes by removing `${{ github.run_id }}`,
  enabling progressive cache hits."
- **Confidence**: settled (first-party reference documentation; this is a documented
  compiler implementation behavior)
- **Quote**: "Fallback mechanism: Compiler generates restore-key prefixes by removing
  `${{ github.run_id }}`, enabling progressive cache hits"
- **Our assessment**: The fallback mechanism is what makes `cache-memory` resilient
  to cold-start situations: when no exact-match cache exists for the current run ID,
  the platform falls back to the most recent cache from the same key prefix. This
  is the mechanism behind why `cache-memory` "just works" for rolling state —
  new runs automatically pick up the most recent prior state even when a prior run's
  exact-match cache has expired. This compiler behavior was not documented in any
  prior source note and explains the practical robustness of `cache-memory` without
  requiring practitioners to configure explicit fallback keys.

### Claim 7: When `tools.github.min-integrity` is configured, cache keys automatically include the workflow's integrity level and policy hash, forcing cache misses when policies change

- **Evidence**: "Integrity-Aware Caching" section states this behavior as automatic
  when `min-integrity` is in use. Four integrity levels with visibility properties
  are documented: merged (sees only merged data), approved (sees approved + merged),
  unapproved (sees all three), none (no integrity filtering).
- **Confidence**: emerging (first-party documentation; the automatic key modification
  is stated but the exact key format is not shown)
- **Quote**: "When workflows use `tools.github.min-integrity`, cache automatically
  isolates by integrity level. Cache keys include the workflow's integrity level and
  policy hash, forcing cache misses when policies change."
- **Our assessment**: Integrity-aware cache isolation prevents cross-contamination
  between integrity levels. An agent operating at `approved` level should not read
  state written by an `unapproved`-level run — the policy hash in the cache key
  enforces this. The "forcing cache misses when policies change" behavior is
  particularly important: when the integrity policy is tightened (e.g., from
  `unapproved` to `approved`), the old cache becomes inaccessible, preventing
  policy upgrades from leaking pre-policy state through cache inheritance. No
  existing source documents that integrity levels affect cache keys. For Ch03:
  document integrity-aware cache isolation as a security property of `cache-memory`
  — the integrity model extends from event filtering to persistent state. The
  four level names here (merged, approved, unapproved, none) match exactly
  `docs-ghaw-integrity-reference.md` Claim 3.

### Claim 8: Shared workflow imports merge cache configurations using three deterministic rules — Single→Single (local overrides), Single→Multiple (local becomes array), Multiple→Multiple (merge by ID, local wins)

- **Evidence**: "Merging from Shared Workflows" section documents three merge rules
  explicitly. These apply when local workflow configs are combined with cache settings
  from imported shared workflow components.
- **Confidence**: settled (first-party reference documentation; three rules are
  explicit with named cases)
- **Quote**: "Merge rules: Single→Single (local overrides), Single→Multiple (local
  becomes array), Multiple→Multiple (merge by ID, local wins)."
- **Our assessment**: The merge semantics matter for teams using shared workflow
  libraries. A shared workflow might provide a default `cache-memory` configuration;
  a local workflow can extend it (adding named caches in the Multiple→Multiple case)
  or override it (Single→Single). The ID-based merge for the Multiple→Multiple case
  means local and shared caches coexist rather than one silently overwriting the
  other. These merge rules are not described in any existing source note. For Ch02:
  document these rules in the shared workflow imports section — they determine how
  cache-memory state is scoped when workflows are composed from library components.

### Claim 9: The maintenance workflow auto-removes outdated cache entries on schedule, keeping only the latest per key prefix group, preventing unbounded growth

- **Evidence**: "Automatic Cleanup" section: "The agentic maintenance workflow
  automatically removes outdated cache entries on schedule, keeping only the latest
  per key prefix group to prevent unbounded growth. Manual cleanup is available
  through the GitHub Actions UI."
- **Confidence**: settled (first-party reference documentation; consistent with
  `docs-ghaw-ephemerals.md` Claim 6)
- **Quote**: "The agentic maintenance workflow automatically removes outdated cache
  entries on schedule, keeping only the latest per key prefix group to prevent
  unbounded growth."
- **Our assessment**: This reference page confirms the ephemerals note's cleanup
  description from the primary spec. The "keep latest per key prefix group" strategy
  combined with the 10GB LRU cap (Claim 1) provides two growth-control layers: the
  maintenance workflow actively deletes older entries per workflow; the platform
  passively evicts LRU entries as the repository-wide cap is approached. Teams
  should not rely solely on LRU as their growth control. For Ch02: document both
  mechanisms as complementary — the maintenance workflow handles per-workflow
  cleanup hygiene; LRU handles repository-wide capacity.

### Claim 10: With threat detection enabled, cache saves follow a validate-before-save sequence (restore→modify→upload→validate→save), blocking persistence of tainted content

- **Evidence**: "Security Considerations" section documents this as a behavioral
  change when threat detection is active.
- **Confidence**: settled (first-party reference documentation; the sequence steps
  are explicitly listed)
- **Quote**: "With threat detection enabled, cache saves only after validation
  succeeds (restore→modify→upload→validate→save sequence)"
- **Our assessment**: This is a security-first cache write protocol: modified cache
  contents are uploaded and validated against the threat detection model before the
  final save commits them to the cache store. An agent that produces tainted output
  (e.g., prompt injection embedded in a scraped document saved to cache) would fail
  validation and have the cache save rejected. This prevents the persistence of
  compromised state across runs. No prior source documents this validate-before-save
  sequence. For Ch03: document as the threat-detection integration point for
  cache-memory — teams using threat detection should know that cache writes may be
  delayed or rejected if contents fail validation.

### Claim 11: The formal error vocabulary for a cache miss is `missing_data` with `reason: "cache_memory_miss"`, which triggers an automatic failure issue via the failure handler

- **Evidence**: Troubleshooting section: "When agents report `missing_data` with
  `reason: \"cache_memory_miss\"`, the failure handler opens an issue. Verify correct
  path usage and key consistency."
- **Confidence**: settled (first-party reference documentation; the exact error JSON
  field names are documented)
- **Quote**: "When agents report `missing_data` with `reason: \"cache_memory_miss\"`,
  the failure handler opens an issue."
- **Our assessment**: This is the first documented error vocabulary for cache-memory
  failures in the corpus. Knowing the exact `reason` field value matters for
  practitioners building monitoring workflows that parse failure-handler issues —
  a `cache_memory_miss` failure should trigger investigation of key consistency and
  path correctness, not a generic agent error response. This also implies a
  diagnostic surface: the failure handler issue will contain context about which
  path and key triggered the miss. For Ch02: add this error pattern to harness
  troubleshooting guidance alongside the remediation steps (verify path usage,
  check key consistency across runs).

### Claim 12: `cache-memory` and `repo-memory` are formally distinct tools with complementary tradeoffs across five dimensions — formally establishing when to choose each

- **Evidence**: "Comparison with Repo Memory" table documents five dimensions:
  Storage (GitHub Actions Cache vs Git Branches), Retention (7 days extendable vs
  Unlimited), Version Control (No vs Yes), Performance (Fast vs Slower), Use Case
  (Temporary/sessions vs Long-term/history).
- **Confidence**: settled (first-party reference documentation; the comparison table
  is the authoritative decision matrix for this platform)
- **Quote**: (no single prose quote; evidence is in the comparison table — see
  Concrete Artifacts)
- **Our assessment**: This formal comparison fills a vocabulary gap. `docs-ghaw-tools-reference.md`
  Claim 5 and `docs-ghaw-memory-ops.md` Claims 2–3 establish that the two tools
  exist with different use cases, but neither provides a structured comparison
  across retention, versioning, and performance dimensions simultaneously. The
  reference page adds a formal decision table: choose cache-memory for
  temporary/session state where speed matters and version history is unnecessary;
  choose repo-memory for long-term/history state where permanence and versioning
  justify the slower performance. For Ch02: use this comparison table as the
  practitioner decision guide for stateful workflow design.

## Concrete Artifacts

### Basic Configuration

```yaml
# Minimal cache-memory configuration — stores at /tmp/gh-aw/cache-memory/
---
tools:
  cache-memory: true
---
```
*Source: gh-aw cache-memory reference documentation, "Basic Configuration" section*

### Advanced Configuration

```yaml
# Advanced options: custom key, extended retention, file-type restriction
---
tools:
  cache-memory:
    key: custom-memory-${{ github.repository_owner }}
    retention-days: 30  # 1-90 days
    allowed-extensions: [".json", ".txt", ".md"]
---
```
*Key note: compiler appends `${{ github.run_id }}` to key automatically.*
*Source: gh-aw cache-memory reference documentation, "Advanced Options" section*

### Multiple Named Caches

```yaml
# Multiple caches with separate IDs, keys, and retention policies
---
tools:
  cache-memory:
    - id: default
      key: memory-default
    - id: session
      key: memory-session-${{ github.run_id }}
    - id: logs
      retention-days: 7
---
```
*Mounts at `/tmp/gh-aw/cache-memory/` (default) or `/tmp/gh-aw/cache-memory-{id}/` (named).*
*Source: gh-aw cache-memory reference documentation, "Multiple Cache Configurations" section*

### Cache Memory vs Repo Memory Comparison Table

| Feature | Cache Memory | Repo Memory |
|---------|--------------|-------------|
| Storage | GitHub Actions Cache | Git Branches |
| Retention | 7 days (extendable) | Unlimited |
| Version Control | No | Yes |
| Performance | Fast | Slower |
| Use Case | Temporary/sessions | Long-term/history |

*Source: gh-aw cache-memory reference documentation, "Comparison with Repo Memory" section*

### Integrity-Aware Cache Isolation

```
When tools.github.min-integrity is configured:
  - Cache keys include workflow's integrity level + policy hash
  - Policy changes force cache misses (old cache inaccessible after policy tightening)

Integrity level visibility:
  merged:     sees only merged data
  approved:   sees approved + merged data
  unapproved: sees all three levels
  none:       no integrity filtering
```
*Source: gh-aw cache-memory reference documentation, "Integrity-Aware Caching" section*

### Shared Workflow Import Merge Rules

```
Single config → Single config:   local overrides
Single config → Multiple config: local becomes array
Multiple config → Multiple config: merge by ID, local wins on conflict
```
*Source: gh-aw cache-memory reference documentation, "Merging from Shared Workflows" section*

### Threat Detection Write Sequence

```
With threat detection enabled:
  restore → modify → upload → validate → save
  (save is blocked if validation fails)
```
*Source: gh-aw cache-memory reference documentation, "Security Considerations" section*

### Troubleshooting Reference

```
Persistence failures:  Verify cache key consistency across runs; check logs for
                       restore/save messages
File access errors:    Create subdirectories first; verify permissions; use absolute paths
Size concerns:         Monitor growth within 10GB limit; use time-based keys for
                       auto-expiration
Cache path problems:   missing_data with reason: "cache_memory_miss" → verify correct
                       path usage and key consistency
```
*Source: gh-aw cache-memory reference documentation, "Troubleshooting" section*

### Storage Backend Summary

```
Storage:     GitHub Actions Cache
Capacity:    10GB per-repository limit
Eviction:    LRU (least-recently-used)
Retention:   7 days default; 1–90 days via retention-days (artifact upload mechanism)
Branches:    Caches accessible across branches
Keys:        Unique per-run save keys; compiler strips run_id for restore-key prefix
```
*Source: gh-aw cache-memory reference documentation, "Behavior and Limitations" section*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-dailyops.md` Claim 6 (`cache-memory: true` at `/tmp/gh-aw/cache-memory/`
    for cross-run state): this reference page authoritatively confirms the path, the
    `true` basic config, and the workflow-scoped key semantics described in the pattern
    guide.
  - `docs-ghaw-audit-with-agents.md` Claim 5 (cache-memory provides persistent state
    at `/tmp/gh-aw/cache-memory/` for rolling trend analysis, 30-day retention): the
    7-day default and `/tmp/gh-aw/cache-memory/` path are formally confirmed;
    `retention-days: 30` in that note's YAML is now explained by Claim 2 (artifact
    upload mechanism for extended retention).
  - `docs-ghaw-expert-ops.md` Claim 6 (`cache-memory: true` enables domain observation
    accumulation): confirmed and extended — the 10GB/LRU constraint (Claim 1) and the
    advanced config options (Claim 4) are the technical substrate behind that pattern.
  - `docs-ghaw-ephemerals.md` Claim 6 (cache-memory cleanup groups by workflow prefix,
    keeps latest run ID, deletes older; key pattern `memory-{workflow}-{run-id}`): the
    reference page's cleanup description ("keeping only the latest per key prefix group")
    is fully consistent with the ephemerals note's detail. The two together give the
    full cleanup picture: the reference page documents the policy; the ephemerals note
    documents the implementation.
  - `docs-ghaw-memory-ops.md` Claim 2 (cache-memory: fast ephemeral storage, GitHub
    Actions cache, 7-day retention): the reference page provides the formal spec for
    what that note described at the conceptual level.
  - `docs-ghaw-tools-reference.md` Claim 5 (two-memory-tool taxonomy; `cache-memory`
    for cross-run trends vs `repo-memory` for repository-specific context): the
    comparison table (Claim 12) formalizes this conceptual distinction across five
    measurable dimensions.
  - `docs-ghaw-integrity-reference.md` Claim 3 (four integrity levels — merged,
    approved, unapproved, none — with cumulative ordering): the integrity-aware caching
    section maps exactly to these four levels, extending integrity coverage from event
    filtering to persistent state.

- **Contradicts**: None identified. All cache-memory behaviors described in existing
  source notes are consistent with this reference page. No contradiction issues to file.

- **Extends**:
  - `docs-ghaw-dailyops.md` + `docs-ghaw-expert-ops.md` + `docs-ghaw-audit-with-agents.md`:
    those pattern guides establish `cache-memory` as the standard cross-run state
    mechanism. This reference page provides the formal specification layer those guides
    assumed but never documented: capacity limits (10GB/LRU), advanced configuration
    options (key, retention-days, allowed-extensions), named multi-cache support,
    integrity isolation, troubleshooting error vocabulary.
  - `docs-ghaw-ephemerals.md` Claim 6: that note documents the cleanup lifecycle
    (keep-latest-per-prefix) and cache key pattern. This reference page extends it
    with the storage backend spec (10GB/LRU), the threat detection write sequence,
    and the formal error vocabulary (`cache_memory_miss`).
  - `docs-ghaw-memory-ops.md` Claim 9 (Pattern 6: use cache-memory for temporary
    session data, repo-memory for metrics/archives): the comparison table (Claim 12)
    formalizes the same recommendation with explicit tradeoff dimensions across
    retention, versioning, and performance.
  - `docs-ghaw-integrity-reference.md`: that note covers integrity level semantics
    for event filtering. This reference page extends integrity coverage to persistent
    state — integrity levels apply not just to what data the agent can process, but
    also to what cache state it can read.

- **Novel**:
  - **10GB per-repository limit with LRU eviction** (Claim 1): No existing source
    names a capacity constraint for cache-memory. First formal storage capacity spec
    in the corpus.
  - **`retention-days: 1–90` via artifact upload mechanism** (Claim 2): The 7-day
    default is established, but the extension mechanism (artifact upload, 1–90 day
    range, decoupled from cache TTL) is entirely new to the corpus.
  - **`allowed-extensions` file-type restriction** (Claim 4): No existing source
    mentions this security configuration option. First documented security config for
    restricting what file types agents can persist in cache-memory.
  - **Multiple named caches with `/tmp/gh-aw/cache-memory-{id}/` path convention**
    (Claim 5): The multi-cache configuration pattern and named-cache path convention
    are new to the corpus.
  - **Compiler-managed fallback key prefixes via `${{ github.run_id }}` stripping**
    (Claim 6): The mechanism enabling cold-start cache hits without manual fallback
    configuration is new and explains why cache-memory is robust by default.
  - **Integrity-aware cache isolation via policy hash in cache key** (Claim 7): No
    existing source documents that integrity levels affect cache key generation and
    can force cache misses on policy changes.
  - **Shared workflow import merge semantics** (Claim 8): Three deterministic merge
    rules (Single→Single, Single→Multiple, Multiple→Multiple) for shared workflow
    cache configs are entirely new to the corpus.
  - **Validate-before-save sequence for threat detection** (Claim 10): The security
    write protocol when threat detection is active is not documented in any existing
    source.
  - **`missing_data` / `cache_memory_miss` error vocabulary** (Claim 11): Formal
    error JSON structure for cache misses is new to the corpus.
  - **Formal Cache Memory vs Repo Memory comparison table** (Claim 12): While the
    conceptual distinction is established, no source provides a formal comparison
    across all five dimensions (storage, retention, version control, performance,
    use case).

## Guide Impact

- **Chapter 02 (Harness Engineering)**:
  - Replace informal `cache-memory` specs scattered across pattern notes with the
    formal specification from this reference page. Add: 10GB/LRU storage constraint
    (Claim 1), `retention-days` extension mechanism with artifact upload semantics
    (Claim 2), named multi-cache pattern with `-{id}/` path conventions (Claims 3, 5),
    advanced config options (`key`, `retention-days`, `allowed-extensions`) (Claim 4),
    and the formal comparison table for `cache-memory` vs `repo-memory` decisions
    (Claim 12).
  - Add the multiple named cache YAML (see Concrete Artifacts) as a harness template
    for workflows managing state at different lifecycle stages.
  - Document the `cache_memory_miss` error vocabulary and remediation steps (Claim 11)
    in the harness troubleshooting section.
  - Document compiler-managed fallback keys (Claim 6) as the mechanism that makes
    cache-memory resilient to cold-starts without manual configuration.
  - Document shared workflow merge semantics (Claim 8) for teams composing workflows
    from shared library components.

- **Chapter 03 (Safety and Verification)**:
  - Add `allowed-extensions` as a defense-in-depth config option for cache-memory
    in security-sensitive workflows (Claim 4).
  - Add integrity-aware cache isolation (Claim 7) as a security property of the
    cache-memory tool — integrity levels extend from event filtering to persistent
    state, and policy tightening forces cache misses. Cross-reference
    `docs-ghaw-integrity-reference.md` Claim 3 for level definitions.
  - Document the validate-before-save sequence (Claim 10) as the threat-detection
    integration point for cache-memory.

- **Chapter 04 (Agent Coordination)**:
  - Add multi-cache configuration (Claim 5) as the mechanism for coordinating
    distinct state stores within a single workflow, each with its own lifecycle.
  - Add shared workflow merge semantics (Claim 8) as the rule set for cache-memory
    composition when coordinating across shared workflow libraries.

## Extraction Notes

1. **Source is formal reference documentation**: This page is in the `reference/`
   URL path section, distinct from `guides/` and `patterns/`. It is the authoritative
   technical specification for `cache-memory`, not a practitioner guide.

2. **WebFetch returned complete content**: All sections were accessible: Overview,
   Basic Configuration, Advanced Options, Multiple Cache Configurations, Behavior
   and Limitations, Integrity-Aware Caching, Merging from Shared Workflows, Comparison
   with Repo Memory, Automatic Cleanup, Security Considerations, Troubleshooting,
   Best Practices.

3. **Retention-days dual-path architecture**: The documentation states `retention-days`
   "uploads artifacts for extended access" — implying a dual-path architecture where
   state can be recovered from either the live cache (fast, 7-day) or uploaded
   artifacts (slower, up to 90 days). The exact artifact format and recovery path
   are not detailed on this page.

4. **No publication date**: The reference documentation page does not carry an
   explicit publication date. Content is consistent with gh-aw platform behavior
   as of the extraction date (May 2026).

5. **Integrity level visibility semantics confirmed**: The four integrity levels
   under "Integrity-Aware Caching" (merged, approved, unapproved, none) match
   exactly the levels documented in `docs-ghaw-integrity-reference.md` Claim 3.
   No contradiction to file.

6. **No contradictions filed**: Reviewed all existing source notes with cache-memory
   coverage (`docs-ghaw-dailyops.md`, `docs-ghaw-expert-ops.md`,
   `docs-ghaw-audit-with-agents.md`, `docs-ghaw-ephemerals.md`,
   `docs-ghaw-memory-ops.md`, `docs-ghaw-tools-reference.md`,
   `docs-ghaw-integrity-reference.md`). No claims in this reference page materially
   oppose any existing source note. All platform behaviors described elsewhere are
   consistent with this specification.
