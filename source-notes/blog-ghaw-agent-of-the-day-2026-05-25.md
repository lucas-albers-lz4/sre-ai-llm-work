---
source_url: https://github.github.com/gh-aw/blog/2026-05-25-agent-of-the-day/
source_type: blog-post
title: "Agent of the Day – May 25, 2026: Architecture Guardian (analysis run)"
author: GitHub Agentic Workflows team (gh-aw), bylined "By Copilot"
date_published: 2026-05-25
date_extracted: 2026-05-26
last_checked: 2026-05-26
status: current
confidence_overall: emerging
issue: "#947"
---

# Agent of the Day – May 25, 2026: Architecture Guardian (analysis run)

> Third "Agent of the Day" entry — profiles a successful Architecture Guardian
> analysis run (no violations found), providing the first concrete breakdown of
> the agent's full execution path: bash pre-step → JSON metrics file →
> violation-classifier sub-agent on a small model → noop or issue. Adds production
> metrics including a 63% prompt cache hit rate and 307 output tokens, and
> introduces the "cheap and reliable" design philosophy, .architecture.yml
> configurable thresholds, and two noise-prevention mechanisms (skip-if-issue-open.md
> deduplication + 2-day issue expiry).

## Source Context

- **Type**: blog-post (third "Agent of the Day" entry from the official GitHub
  Agentic Workflows blog; each post profiles a single production agent with concrete
  run data. This entry and the May 20 entry both feature Architecture Guardian —
  May 20 showed a quiet-day skip-when-idle run; this entry shows a complete analysis
  run where files were modified in the last 24 hours and the agent ran the full
  scan, finding no violations. Together they document both execution paths of the
  same agent. Post is bylined "By Copilot" — the recurring gh-aw convention for
  posts authored with the platform's AI.)
- **Author credibility**: The gh-aw blog is the official publication of GitHub's
  Agentic Workflows platform team (GitHub Next / Microsoft Research). The run ID
  cited (26407385057) is a specific, independently verifiable GitHub Actions run.
  Metrics (3.8-minute runtime, 121,425 input tokens, 75,961 cache reads, 307 output
  tokens, 3 AI turns, 4 API calls) are instrumentation data from the live
  `github/gh-aw` production repository. High credibility for first-party platform
  claims.
- **Scope**: Profiles the Architecture Guardian's analysis-path execution (run
  26407385057) — a run where relevant files were found in the last 24 hours, the
  full scan was performed, and no violations were detected. Documents the complete
  three-phase execution model (bash pre-step, violation-classifier sub-agent, output
  action), severity tiers with thresholds, token economics, and noise-prevention
  mechanisms. Does NOT cover: a run where violations ARE found and an issue is opened
  (only the issue-opening behavior is described, not shown with run data); the
  specific contents of .architecture.yml; the violation-classifier sub-agent's
  frontmatter configuration; or the YAML workflow definition for Architecture Guardian.

## Extracted Claims

### Claim 1: A bash pre-step gathers all metrics before the agent runs — calling `git log --since="24 hours ago"` to build the file list, then computing line counts, function sizes, export counts, and running `go list ./...` for import cycles, with results written to `/tmp/gh-aw/agent/arch-metrics.json`

- **Evidence**: Direct description of the pre-step mechanics in the source, with the
  exact command, the computed metrics, and the output file path provided (via the
  Prospector triage comment citing post content).
- **Confidence**: settled (first-party production implementation detail; bash pre-step
  mechanics and file path are explicitly named)
- **Quote**: "A bash pre-step calls `git log --since="24 hours ago"` to build the file
  list. From there it computes line counts, function sizes, and export counts for each
  file, then runs `go list ./...` to catch import cycles before they calcify."
- **Our assessment**: This is a live production instance of the `/tmp/gh-aw/agent/`
  data-exchange pattern documented in `docs-ghaw-deterministic-agentic-patterns.md`
  Claim 3. The bash pre-step offloads all deterministic metric collection to a
  shell script, leaving the AI agent to reason over structured JSON rather than
  performing file enumeration itself. "Before they calcify" is the framing — import
  cycles are cheap to detect early and expensive to unwind late. The pattern is
  reusable: any agent that needs to scan a repository can use a bash pre-step to
  gather file-system facts, write JSON, and let the agent focus on interpretation.
  For Ch02 (Harness Engineering): Architecture Guardian is the canonical concrete
  example of the bash-pre-step → `/tmp/gh-aw/agent/<file>.json` → agent pattern.

### Claim 2: A lightweight violation-classifier sub-agent running on a small model reads the JSON metrics and applies severity classification — separating data gathering (bash) from classification (sub-agent) from full reasoning (agent)

- **Evidence**: Direct description in the source with explicit small-model claim.
- **Confidence**: settled (first-party; the sub-agent name, its input, and its model
  size class are all named)
- **Quote**: "A lightweight sub-agent — `violation-classifier`, running on a small
  model — reads that JSON and applies a three-tier severity ladder"
- **Our assessment**: This is a production example of the per-sub-agent model selection
  pattern documented in `docs-ghaw-inline-sub-agents.md` Claim 4: the parent workflow
  (likely running a capable model for the overall reasoning task) delegates the
  bounded JSON-to-severity classification to a smaller, cheaper model. The
  `violation-classifier` name is role-indicating (following the naming convention in
  `docs-ghaw-inline-sub-agents.md` Claim 7). The three-stage execution model that
  results — bash pre-step (deterministic, shell) → violation-classifier (classification,
  small model) → parent agent (decision and action) — is a cost-conscious, separation-of-
  concerns architecture that no existing corpus note describes in this explicit form.
  For Ch02: document this three-stage chain as a named cost optimization pattern for
  agents that analyze structured data: collect deterministically, classify cheaply,
  decide with the capable model.

### Claim 3: The violation-classifier applies a three-tier severity ladder with specific thresholds: BLOCKER (files >1,000 lines or any import cycle), WARNING (files >500 lines or functions >80 lines), INFO (files exporting >10 identifiers)

- **Evidence**: Direct description in the source with specific threshold values.
- **Confidence**: settled (first-party; thresholds are explicitly named and quantified)
- **Quote**: "**BLOCKER** — files exceeding 1,000 lines or any import cycle / **WARNING** — files over 500 lines or functions over 80 lines / **INFO** — files exporting more than 10 identifiers"
- **Our assessment**: The three thresholds are grounded in practical heuristics:
  1,000-line files are legitimately problematic in most codebases (a blocker worth
  stopping for); 500-line files are worth reviewing but not immediately dangerous;
  80-line functions are commonly cited as a readability threshold; 10-identifier
  exports suggest an overly broad public interface. The BLOCKER/WARNING/INFO naming
  mirrors standard alerting severity conventions, making the output immediately
  actionable for teams already familiar with those terms. For Ch02: these thresholds
  are a concrete, adoptable starting point for teams building code quality agents.
  For Ch04 (Operations): the three-tier output is the type schema that the safe-output
  action (file issue or noop) dispatches on — a bounded classifier output enabling
  clean conditional logic downstream.

### Claim 4: Violation thresholds are configurable per team via `.architecture.yml`, enabling teams to tune the severity ladder without modifying the workflow

- **Evidence**: Direct description in the source.
- **Confidence**: settled (first-party; configuration file named explicitly)
- **Quote**: "Thresholds live in `.architecture.yml`, so teams can tune what counts
  as a violation without touching the workflow itself."
- **Our assessment**: The separation of thresholds (in `.architecture.yml`) from
  workflow logic (in the workflow `.md` file) is the configuration-driven automation
  pattern: behavior is parameterized, not hardcoded. This enables a team inheriting
  or sharing the Architecture Guardian workflow to adjust the 1,000-line BLOCKER to
  2,000 lines for their larger codebase without forking the workflow definition.
  For Ch02: document `.architecture.yml`-style externalized threshold configuration
  as the recommended pattern for automations that encode quality thresholds — any
  value that a team might reasonably want to adjust should be in a config file, not
  hardcoded in the agent prompt.

### Claim 5: Two distinct noise-prevention mechanisms keep the issue tracker clean: a shared `skip-if-issue-open.md` import prevents duplicate issue filing, and a 2-day issue expiry via `daily-issue-base.md` removes stale violations

- **Evidence**: Direct description of both mechanisms in the source.
- **Confidence**: settled (first-party; both import file names and behaviors explicitly
  stated)
- **Quote**: "There's also a guard against noise: a shared `skip-if-issue-open.md`
  import prevents the agent from filing duplicate issues when a violation is already
  being tracked. The 2-day expiry on issues (via `daily-issue-base.md`) keeps the
  tracker clean."
- **Our assessment**: The two mechanisms address complementary noise failure modes.
  Deduplication (skip-if-issue-open) prevents the same violation from being re-filed
  on each daily run while it remains open — without it, a persistent 1,200-line file
  would generate a new BLOCKER issue every weekday. Expiry (daily-issue-base.md)
  prevents resolved-but-unclosed issues from lingering indefinitely — without it,
  the Architecture Guardian's issues would accumulate even after teams fix violations.
  Both mechanisms are implemented as shared `.md` imports, which is the gh-aw
  convention for reusable cross-workflow logic (see `docs-ghaw-guides-reusing-workflows.md`).
  For Ch02: document the deduplication + expiry pair as the two-mechanism noise
  management pattern for daily analysis workflows. An agent that runs daily and
  creates issues needs both — deduplication alone creates issues that never age out;
  expiry alone re-creates issues that were already opened.

### Claim 6: The Architecture Guardian achieves a 63% prompt cache hit rate across daily runs, with 75,961 of 121,425 input tokens served from cache, because the workflow instructions are stable while only the file list and metrics change

- **Evidence**: Specific metrics from run 26407385057.
- **Confidence**: settled (specific measured metric from production run)
- **Quote**: "121,425 input tokens processed, but 75,961 of those came from cache
  reads. That's roughly 63% cache hit rate"
- **Our assessment**: The 63% cache hit rate is structurally explained by the agent's
  design. The workflow instructions — the BLOCKER/WARNING/INFO severity rules, the
  file scope (modified `.go`, `.js`, `.cjs`, `.mjs`), the issue-creation procedure —
  are identical from one daily run to the next. These stable instruction blocks fill
  the cache on the first run and are reused on subsequent runs. Only the
  `arch-metrics.json` content (the file list and computed metrics) changes between
  runs. This matches the caching principle from `blog-anthropic-prompt-caching-everything.md`
  Claim 1: stable context at the top of the prompt, variable data at the bottom.
  For Ch03 (Cost and Operations): scheduled agents with stable instructions are
  natural candidates for high cache hit rates. Design the prompt so stable rule
  definitions and behavior instructions appear before the per-run variable data.

### Claim 7: The analysis run produces only 307 output tokens — an extremely low output:input ratio (0.25%) demonstrating that analysis agents can be highly cost-efficient when their output is a structured verdict rather than explanatory prose

- **Evidence**: Specific metric from run 26407385057.
- **Confidence**: anecdotal (one run with no violations found; a violation-found run
  producing a structured issue report would likely have more output tokens)
- **Quote**: "307 output tokens."
- **Our assessment**: 307 output tokens on 121,425 input tokens is a ~0.25%
  output:input ratio. When the agent finds no violations, it has nothing to explain —
  a verdict of "no violations" is short. This is the opposite of a content-generating
  agent (summarizers, writers) where output can approach or exceed input. Analysis
  agents that produce structured pass/fail verdicts have systematically lower output
  costs than agents that produce prose. For Ch03: design analysis agents to emit
  structured, minimal output — a severity-tiered verdict with file names is cheaper
  than a narrative summary of findings. The 307-token data point is a useful reference
  for estimating costs on zero-finding runs.

### Claim 8: The complete analysis run uses 3 AI turns and 4 GitHub API calls — the same turn count as the May 20 quiet-day skip run, suggesting the agent's reasoning overhead is fixed regardless of whether files are present

- **Evidence**: Specific metrics from run 26407385057.
- **Confidence**: anecdotal (one run; both the no-files-changed path and the
  files-changed-no-violations path used 3 turns — a third data point would be a
  violations-found run)
- **Quote**: "Total AI turns: 3. GitHub API calls: 4"
- **Our assessment**: The May 20 run (no relevant files changed, agent decided to skip)
  also used 3 turns. This May 25 run (files changed, analysis ran, no violations)
  also used 3 turns. This suggests the Architecture Guardian's main agent job has a
  fixed 3-turn structure regardless of whether the skip decision or the analysis path
  is taken. The turn count may only increase on a violations-found run (the third,
  unobserved path) where the agent must construct a structured issue report. For
  Ch04 (Operations): comparing turn counts across run types (skip, no-violation, violation)
  is a signal for understanding which path was taken. If 3 is the baseline for both
  skip and no-violation paths, and a violation-found run uses 5 turns, the turn count
  becomes a proxy for "did the agent find anything to report."

### Claim 9: The Architecture Guardian is designed to be "cheap and reliable" rather than "clever" — the goal is consistent, low-cost detection of accumulating drift, not sophisticated architectural reasoning

- **Evidence**: Author's explicit characterization of the design philosophy.
- **Confidence**: emerging (author framing; the "cheap and reliable" philosophy is
  stated as intent, not measured against alternatives)
- **Quote**: "The Architecture Guardian isn't trying to be clever. It's trying to be
  _cheap and reliable_"
- **Our assessment**: This design philosophy is distinct from the "automation maturity"
  framing in `blog-ghaw-agent-of-the-day-2026-05-20.md` Claim 10, though complementary.
  The May 20 post defined maturity as knowing when NOT to run ("doing only the work
  that matters"). This post defines the agent's posture as minimizing reasoning
  complexity ("cheap and reliable" over "clever"). Together: a mature automated agent
  is one that (a) only runs when there is something to check, and (b) applies the
  cheapest sufficient reasoning to check it. For Ch02: "cheap and reliable" is a
  named design target for analysis automation — resist the temptation to make the
  agent do sophisticated reasoning when a classifier sub-agent and a JSON file will
  suffice.

### Claim 10: When violations are found, the agent opens a GitHub issue with structured reporting tagged `architecture`, `automated-analysis`, and `cookie`; when no violations are found, it calls noop — the binary outcome is the interface between the agent and the issue tracker

- **Evidence**: Direct description of the two outcome paths.
- **Confidence**: settled (first-party; both paths and the issue labels are named
  explicitly)
- **Quote**: "If it finds something, it opens a GitHub issue with a structured report,
  tagged `architecture`, `automated-analysis`, and `cookie`. If not, it calls noop
  and gets out of the way."
- **Our assessment**: The binary issue-or-noop interface is clean. The agent's
  output contract has exactly two states: a structured issue (actionable) or silence
  (no action required). The label set `architecture` + `automated-analysis` +
  `cookie` provides searchability and category tagging — the `architecture` label
  makes issues filterable by domain; `automated-analysis` marks the provenance
  (not human-filed); `cookie` appears to be a gh-aw internal ownership or
  workflow-type marker. For Ch02: the binary output contract (issue or noop) is a
  pattern for analysis agents — avoid intermediate outputs (warnings, "consider
  reviewing" messages) that do not map to a clear action. An issue means "someone
  must act"; noop means "nothing to act on." Ambiguous output states erode trust.

### Claim 11: Architectural drift accumulates incrementally "like sediment" — teams do not choose drift, it accumulates when no lightweight automatic noticing mechanism exists

- **Evidence**: Closing paragraph of the post.
- **Confidence**: anecdotal (author framing; the sediment metaphor is a
  characterization, not a measured finding)
- **Quote**: "I've seen codebases where large files and tangled imports accumulate
  like sediment — not because anyone chose it, but because nobody had a lightweight,
  automatic way to notice. This workflow is that noticing mechanism. It doesn't replace
  a thoughtful architecture review. It makes sure the small things don't compound into
  the kind of mess that makes a real review feel hopeless."
- **Our assessment**: The "sediment" metaphor is precise: sediment accumulates through
  deposition, not decisions. No engineer chooses to make a file grow to 2,000 lines;
  each individual PR adds 20 lines and passes review without concern. After 90 PRs the
  file is a maintenance problem. The Architecture Guardian is designed to surface each
  incremental step — each PR's contribution to drift — before it compounds. The
  closing "It doesn't replace a thoughtful architecture review" is important: the agent
  is positioned as a complement to human review, not a substitute. For Ch05 (Team
  Adoption): the sediment framing is a persuasion argument for teams considering
  automated architectural monitoring — "your team isn't failing, you just lack the
  noticing layer."

## Concrete Artifacts

### Architecture Guardian: Run Profile (analysis run — no violations)

```
Agent:          Architecture Guardian (GitHub Agentic Workflows, github/gh-aw repository)
Run ID:         26407385057
Outcome:        noop (analysis completed; no violations detected)
Runtime:        3.8 minutes

Token economics:
  Input tokens:     121,425
  Cache reads:       75,961  (63% cache hit rate)
  Output tokens:        307  (0.25% output:input ratio)

Execution profile:
  AI turns:           3
  GitHub API calls:   4

Files scanned:  Modified .go, .js, .cjs, .mjs files from past 24 hours
                (excluding tests and vendor directories)
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – May 25, 2026"*

### Architecture Guardian: Three-Stage Execution Model (analysis path)

```
Stage 1 — bash pre-step (deterministic, shell):
  git log --since="24 hours ago"  → file list
  line count computation           → per-file metric
  function size measurement        → per-file metric
  export count                     → per-file metric
  go list ./...                    → import cycle detection
  Output: /tmp/gh-aw/agent/arch-metrics.json

Stage 2 — violation-classifier sub-agent (small model, classification):
  Input:  arch-metrics.json
  Apply three-tier severity ladder:
    BLOCKER  — files > 1,000 lines OR any import cycle
    WARNING  — files > 500 lines OR functions > 80 lines
    INFO     — files exporting > 10 identifiers
  Output: classified violation list (or empty)

Stage 3 — parent agent (decision + action):
  If violations found:
    Open GitHub issue with structured report
    Apply labels: architecture, automated-analysis, cookie
    Guard: skip-if-issue-open.md (deduplication)
  If no violations:
    Call noop ("gets out of the way")

Configuration:
  Thresholds:  .architecture.yml (team-tunable)
  Issue expiry: daily-issue-base.md (2-day TTL)
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – May 25, 2026"*

### Architecture Guardian: Noise-Prevention Mechanism Pair

```
Mechanism 1 — Deduplication (skip-if-issue-open.md):
  Problem:  A persistent violation would generate a new issue on every daily run
  Solution: Before filing, check if an issue is already open for this violation
  Effect:   Each violation is filed once; stays open while unresolved

Mechanism 2 — Issue expiry (daily-issue-base.md):
  Problem:  Resolved violations leave stale open issues in the tracker
  Effect:   Issues auto-close after 2 days if not renewed by the agent
  Pattern:  Violation must be re-detected each day to keep the issue alive
```

*Source: GitHub Agentic Workflows blog, "Agent of the Day – May 25, 2026"*

## Cross-References

- **Corroborates**:
  - `docs-ghaw-deterministic-agentic-patterns.md` Claim 3 (`/tmp/gh-aw/agent/` is the
    designated data-exchange directory between deterministic pre-processing jobs and the
    AI agent): The Architecture Guardian's bash pre-step writes to
    `/tmp/gh-aw/agent/arch-metrics.json` (Claim 1 here), which is exactly the hand-off
    mechanism that claim documents. This is the most concrete production example of
    that pattern in the corpus — a named file, a named command (`git log --since="24
    hours ago"`), and a named agent that reads it.
  - `docs-ghaw-inline-sub-agents.md` Claim 4 (the `model` field in sub-agent frontmatter
    enables per-sub-agent model selection; the parent can run on an expensive model while
    delegating bounded tasks to a cheaper one): The `violation-classifier` sub-agent
    (Claim 2 here) explicitly "runs on a small model," providing the first production
    example in the corpus of this cost-optimization pattern in a real workflow. The
    docs-ghaw-inline-sub-agents note documented the mechanism; this source demonstrates
    the usage.
  - `blog-ghaw-agent-of-the-day-2026-05-20.md` Claim 10 ("automation maturity" = doing
    only the work that matters): The "cheap and reliable" design philosophy (Claim 9
    here) is the intra-agent analog to May 20's inter-agent skip logic. May 20 said
    "mature agents skip unnecessary runs"; this note says "mature agents use the cheapest
    sufficient reasoning inside each run." Both arrive at the same principle from
    different angles.
  - `blog-anthropic-prompt-caching-everything.md` Claim 1 (stable context at the top
    of the prompt, variable data later, maximizes cache reuse): The 63% cache hit rate
    (Claim 6 here) is structurally explained by exactly this principle — the Architecture
    Guardian's severity rules and behavior instructions are stable across daily runs;
    only the `arch-metrics.json` content changes. The hit rate is the observable outcome
    of applying the caching principle correctly.

- **Extends**:
  - `blog-ghaw-agent-of-the-day-2026-05-20.md`: That note profiled Architecture Guardian's
    skip path (quiet-day noop run, run 26171885477: no relevant files changed → 3 turns
    to decide to skip → call noop). This note profiles the analysis path (files changed →
    bash pre-step runs → violation-classifier runs → no violations found → call noop, run
    26407385057). Together they document both main execution paths of the same agent.
    A third path remains unobserved: a violations-found run where the agent opens a
    GitHub issue. The May 20 Claim 6 quote ("it never writes back to GitHub") was
    imprecise — it described the noop path only; the May 25 source reveals the agent
    DOES open issues on the violations-found path. See Extraction Note 4.
  - `docs-ghaw-inline-sub-agents.md`: That note documented inline sub-agents as a
    composition pattern and the `model` field as a cost lever. This source adds the
    first named production sub-agent (`violation-classifier`, small model, JSON-to-
    severity classification) that demonstrates the pattern with specific role, input,
    and model class. The connection between inline sub-agents and the classification
    use case is now concrete.
  - `docs-ghaw-code-quality-monitoring.md`: That note covers multi-language code quality
    monitoring (ESLint, flake8, Dependabot) using the side-repo pattern, with a
    three-part issue aggregation rule. This source adds: (a) a severity tier ladder
    (BLOCKER/WARNING/INFO) as an output schema for code quality violations, (b)
    sub-agent classification as a cost-efficient tier-assignment mechanism, and (c)
    the deduplication + expiry noise-prevention pair. Together, they provide
    complementary approaches to the same domain.

- **Contradicts**: No formal contradiction issue filed. The May 20 note characterized
  Architecture Guardian as "never writes back to GitHub," which is imprecise: the
  violations-found path does create GitHub issues. The imprecision arose because May 20
  profiled only a noop run. No guide advice changes as a result — both notes agree the
  agent does not modify code or open PRs, and creates informational issues. See
  Extraction Note 4 for the full analysis.

- **Novel**:
  - **Three-stage execution chain** (Claim 1–2): The bash pre-step → violation-classifier
    sub-agent → parent agent chain is not described as a named pattern in any existing
    corpus note. It combines two documented patterns (`/tmp/gh-aw/agent/` data exchange
    + per-sub-agent model selection) in a specific three-stage architecture for analysis
    workflows.
  - **violation-classifier as first named production sub-agent** (Claim 2): No prior
    corpus source names a specific production sub-agent, its role, and its model class.
    `violation-classifier` (small model, JSON-to-severity classification) is the first.
  - **BLOCKER/WARNING/INFO severity tier thresholds** (Claim 3): Specific numerical
    thresholds for architectural violation severity (1,000 lines BLOCKER, 500 lines
    WARNING, 80-line function WARNING, 10-identifier INFO) are not documented in any
    existing source note. `docs-ghaw-code-quality-monitoring.md` Claim 5 documents
    different thresholds for ESLint/flake8 (>5 errors, >10 errors, >500 lines) in a
    different context; the BLOCKER/WARNING/INFO schema is new.
  - **`.architecture.yml` configurable threshold file** (Claim 4): The pattern of
    externalizing quality enforcement thresholds to a team-owned config file, separate
    from the workflow itself, is not documented in any existing corpus note.
  - **Deduplication + expiry as the two-mechanism noise-prevention pair** (Claim 5):
    The skip-if-issue-open.md + daily-issue-base.md combination as a complementary
    pair (deduplicate forward, expire backward) is not documented in any existing
    corpus note.
  - **63% prompt cache hit rate as a concrete scheduled-agent benchmark** (Claim 6):
    No prior corpus source provides a measured cache hit rate for a scheduled analysis
    agent. The 63% figure is a production data point for practitioners estimating
    caching returns on similar workflows.
  - **307-token output metric for zero-finding analysis runs** (Claim 7): No prior
    source documents output token count as a metric for understanding analysis agent
    output cost. The 307-token data point introduces output:input ratio as a cost
    signal distinct from input token count alone.
  - **"Sediment" framing for architectural drift** (Claim 11): The metaphor of drift
    accumulating as sediment — through deposition, not decisions — is not found in any
    existing corpus source. It is a precise and persuasive team-adoption argument.

## Guide Impact

- **Chapter 02 (Harness Engineering)**:
  - Add the bash pre-step → JSON → sub-agent → agent three-stage chain as a named
    cost-optimization pattern for analysis workflows (Claims 1–2). Architecture Guardian
    is the canonical concrete example: use `git log` in a bash pre-step to gather facts
    deterministically, write JSON to `/tmp/gh-aw/agent/`, have a small-model sub-agent
    classify the structured output, and reserve the capable agent model for the final
    decision and action. This pattern is more cost-efficient than having the capable
    model gather files, classify violations, and decide actions in one reasoning chain.
  - Document `.architecture.yml`-style externalized threshold configuration as the
    recommended pattern for automated enforcement workflows (Claim 4). Any threshold
    value that a team might reasonably want to adjust should be in a separate config
    file, not embedded in the agent instructions. This enables sharing and inheriting
    workflows without forking.
  - Add binary output contract (issue or noop) as the recommended agent interface design
    for analysis agents (Claim 10). Agents that produce intermediate or ambiguous outputs
    ("consider reviewing file X") erode trust; agents with two clearly actionable states
    (issue = act, noop = no action needed) maintain signal integrity.

- **Chapter 03 (Cost and Operations)**:
  - Add the deduplication + expiry pair as the two-mechanism noise-prevention pattern
    for daily analysis workflows (Claim 5). Document alongside the per-category
    aggregation rule from `docs-ghaw-code-quality-monitoring.md` Claim 6 as the
    complete noise-prevention toolkit for analysis workflows.
  - Add scheduled agent cache hit rate optimization: design prompts with stable
    instruction blocks before per-run variable data to maximize cache reuse (Claim 6).
    The 63% hit rate from Architecture Guardian is a production benchmark. Pair with
    `blog-anthropic-prompt-caching-everything.md` Claim 1 as the principle behind
    the result.

- **Chapter 04 (Multi-Agent Patterns / Sub-Agents)**:
  - Add `violation-classifier` as the first named production sub-agent example in the
    corpus (Claim 2). It demonstrates: bounded classification input (structured JSON),
    small model selection (classification task does not require reasoning capability),
    and named role (role-indicating name as convention). Use as a teaching example
    alongside `docs-ghaw-inline-sub-agents.md` Claims 4 and 7.
  - Document BLOCKER/WARNING/INFO as a reusable severity tier schema for code quality
    agents, with the specific Architecture Guardian thresholds as a starting point
    practitioners can tune (Claims 3–4).

- **Chapter 05 (Team Adoption)**:
  - Add the "sediment" framing for architectural drift as a team-adoption argument
    (Claim 11): "Your team isn't failing — you just lack the noticing layer." The
    Architecture Guardian's value is that it surfaces each incremental drift contribution
    before it compounds. This reframes automated architectural monitoring from "enforcement"
    (punitive) to "noticing" (enabling) — a more effective adoption posture.
  - Add "cheap and reliable over clever" as a design target for analysis automation
    (Claim 9): teams considering custom agents often over-specify sophisticated reasoning
    when a classifier sub-agent and a JSON file will achieve the goal more cheaply and
    reliably. The Architecture Guardian is the teaching example.

## Extraction Notes

1. **Third "Agent of the Day" format entry**: The May 15 entry (AI Moderator,
   `blog-ghaw-agent-of-the-day-2026-05-15.md`) and May 20 entry (Architecture Guardian,
   `blog-ghaw-agent-of-the-day-2026-05-20.md`) were extracted earlier. This is the
   third entry. Notably, both May 20 and May 25 feature Architecture Guardian — two
   different runs of the same agent on different execution paths (skip path vs. analysis
   path).

2. **Multiple WebFetch passes for verbatim quotes**: Three targeted WebFetch passes
   were made with progressively more targeted prompts. The quotes in this note were
   consistent across passes. The WebFetch tool processes through a small AI model;
   character-for-character verification against the HTML source was not possible. Claims
   where no stable quoted passage was returned are marked "(no direct quote; see
   paraphrase in Our assessment)."

3. **Run 26407385057 is an analysis run, not a skip run**: The May 20 post (run
   26171885477) showed the architecture guardian deciding to skip because no relevant
   files changed in 24 hours. This run found relevant files, ran the full analysis, and
   found no violations. The two runs together document the skip path and the no-violations
   analysis path. A third path — violations found, issue opened — is described in the
   post but not demonstrated with run data.

4. **May 20 "read-only" characterization is imprecise**: `blog-ghaw-agent-of-the-day-2026-05-20.md`
   Claim 6 states "Architecture Guardian operates in read-only mode—it never writes back
   to GitHub, never auto-fixes violations, never opens PRs." This May 25 source reveals
   the agent DOES write to GitHub on the violations-found path by opening informational
   issues. The May 20 post was profiling only a noop run and did not show the
   violations-found path. The "read-only" characterization was intended to distinguish
   Architecture Guardian from agents that auto-fix code or open PRs with code changes;
   it was not intended as a universal claim about all GitHub writes. No formal
   contradiction issue was filed because: (a) both notes agree the agent does not modify
   code or open PRs; (b) the imprecision arose from an incomplete execution path profile,
   not a material factual conflict; (c) no practitioner reading both notes would receive
   conflicting design guidance. The guide should characterize Architecture Guardian as
   "read-only toward code modifications" (never modifies source code, never opens code-
   change PRs) rather than "never writes to GitHub."

5. **No sub-pages followed**: The blog post does not link to Architecture Guardian's
   workflow YAML or to `.architecture.yml` documentation. The source is self-contained.
   The `.architecture.yml` file is referenced but its schema is not documented in this
   post.

6. **No contradictions filed**: Reviewed `blog-ghaw-agent-of-the-day-2026-05-20.md`,
   `docs-ghaw-deterministic-agentic-patterns.md`, `docs-ghaw-inline-sub-agents.md`, and
   `docs-ghaw-code-quality-monitoring.md`. The May 20 "read-only" imprecision (Extraction
   Note 4) does not rise to a formal contradiction. No contradiction issue filed.
