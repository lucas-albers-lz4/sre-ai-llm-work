---
source_url: https://langfuse.com/docs/evaluation/get-started/online
source_type: docs
title: "Evaluate Production Traffic — Langfuse"
author: "Langfuse (Langfuse GmbH / Finto Technologies Inc.)"
date_published: n.d. (living documentation; copyright footer 2022–2026, current as of 2026-09-03)
date_extracted: 2026-09-03
last_checked: 2026-09-03
status: current
confidence_overall: emerging
issue: "#1185"
---

# Evaluate Production Traffic — Langfuse

> The vendor operational how-to for running always-on (online) LLM evaluation on
> live production traces: the **Rule** primitive (filters + sampling rate +
> one-or-more evaluators) as the production scoring-scoping mechanism, a
> **cost-aware sampling** lever for LLM-as-a-Judge (review 7-day matching volume
> and *estimated judge cost*, lower sampling rate if needed), the
> **test-the-judge-first** loop before attaching a rule, and **batch evaluation**
> of historical observations as the complement to continuous scoring. Supplies the
> concrete rollout/cost-governance mechanics that the existing core-concepts note
> (#195) covers only conceptually.

## Source Context

- **Type**: docs (vendor configuration how-to — "Evaluate Production Traffic")
- **Author credibility**: Langfuse is a widely-used open-source LLM observability
  platform (tracing, prompt management, evaluation). This page is first-party,
  Markdown-first documentation of its shipped online-evaluation feature. Claims
  about what the product does (rule semantics, sampling-rate cost control, the
  UI workflow) are authoritative for the tool's intended operation; they are
  vendor-authored and not independently benchmarked. Concrete may change as the
  product evolves (living docs, © 2022–2026).
- **Scope**: Covers (1) agentic install paths (Agent Skill / Cursor plugin /
  npm CLI), (2) the manual UI setup workflow — create an evaluator → test on
  sample observations → attach a rule → see scores, (3) the Rule primitive
  (filters + sampling rate + one or more evaluators), (4) the 7-day volume /
  estimated-cost review with sampling as the cost lever for LLM-as-a-Judge, (5)
  batch evaluation of historical observations, (6) a troubleshooting entry for an
  observation-level evaluator not executing, and (7) links to other live-scoring
  methods (Scores via UI / annotation queues, user feedback, Scores via API/SDK).
  Does NOT cover: the offline/online eval-loop concept, the Score data model, the
  five-method taxonomy, or the judge-prompt structure — those are deliberately
  deferred to `docs-langfuse-evaluation-core-concepts.md` (#195). This page is
  tightly scoped to the *setup mechanics* of online scoring.
- **Linked pages**: The page links to Core Concepts (evaluators-and-rules),
  LLM-as-a-Judge, Code evaluators, score analytics, custom dashboards, batch
  evaluation, and the FAQ troubleshooting page ("Why is my observation-level
  evaluator not executing?"). The triage and the existing #195/#196 notes already
  cover the concept/taxonomy and dataset sides; this note extracts the page's own
  page-local claims and the troubleshooting angle rather than re-extracting the
  linked concept pages.

## Extracted Claims

### Claim 1: A Rule is the production scoring-deployment primitive — it defines which incoming observations get scored via filters, a sampling rate, and one or more evaluators
- **Evidence**: The "Attach a rule to incoming traces" step, which defines the
  Rule and the three components that scope what live traffic gets scored.
- **Confidence**: settled
- **Quote**: "A rule defines **which** incoming observations are scored: filters, sampling rate, and one or more evaluators."
- **Our assessment**: This is the concrete scoping/gating mechanism that #195
  (Claim 6, observation-level online eval) frames conceptually. The Rule is how
  you bind evaluators to a *filtered* stream of live observations and scale them
  by sampling — the deployment-time control that keeps an always-on judge from
  scoring every trace and blowing up cost. This is the missing operational layer
  in the corpus's online-eval coverage.

### Claim 2: Before enabling an online rule, review the matching volume from the past seven days; for LLM-as-a-Judge also review the estimated cost and lower the sampling rate if needed — sampling rate is the primary cost-control dial for always-on judging
- **Evidence**: The same "Attach a rule" step's guidance to review 7-day matching
  volume and, for LLM-as-a-Judge, to review estimated cost and lower sampling.
- **Confidence**: emerging
- **Quote**: "Review the matching volume from the past seven days. For LLM-as-a-Judge, also review the estimated cost and lower the sampling rate if needed."
- **Our assessment**: This is the genuinely new, SRE-flavored pattern in the
  source. The cost of a continuously-running LLM judge is proportional to how much
  live traffic it scores, so Langfuse exposes a *pre-enable preview* (7-day
  volume + estimated cost) and a *sampling-rate knob* to bring that cost under
  control before a rule goes live. #195's Claim 6 advised scoping judges to
  observation level to cut volume/cost but never named sampling as the ongoing
  control. Worth pulling into Ch02/Ch05 as the production cost-governance pattern
  for always-on judging.

### Claim 3: The recommended production rollout is create-evaluator → test/iterate on representative sample observations → then attach a rule — the judge is validated against real production observations before it ever scores live traffic
- **Evidence**: The three-step Manual setup workflow (Create an evaluator / Test
  on sample observations / Attach a rule to incoming traces). The test step says
  to filter to representative observations, run the evaluator, and iterate until
  the result matches expectation.
- **Confidence**: emerging
- **Quote**: "On the right, filter to representative production observations, select one, and run the evaluator to test and iterate until the result matches what you would expect."
- **Our assessment**: A production-safety loop: author the evaluator against
  real, representative observations and iterate until the output is trustworthy
  *before* attaching a rule that makes it score live traffic. This is validation-
  before-live-exposure, analogous to testing a change in staging before prod — a
  reasonable, low-risk pattern worth recommending in Ch05's eval-rollout guidance.

### Claim 4: New matching observations receive scores as they arrive once a rule is attached; scored observations can be inspected and the metric watched over time via score analytics or a custom dashboard
- **Evidence**: The "See scores on production traces" step.
- **Confidence**: emerging
- **Quote**: "New matching observations receive scores as they arrive. Open a scored observation to inspect the value and the judge's reasoning, then use [score analytics] or a [custom dashboard] to watch the metric over time."
- **Our assessment**: Closes the online-eval loop at the monitoring layer: the
  score becomes a time-series signal (with the judge's stated reasoning attached)
  that can be visualized on a dashboard — corroborating the evaluator-as-monitorable-
  signal thesis of #195 (Claim 11) and #284 (score analytics). The judge's
  "reasoning" being attached to each score is a nice explainability touch for
  debugging a bad score.

### Claim 5: The same evaluator can be run over selected historical observations via batch evaluation, as a complement to always-on online scoring
- **Evidence**: The "See scores on production traces" step's note about batch
  evaluation.
- **Confidence**: emerging
- **Quote**: "You can also run the same evaluator on selected historical observations with [batch evaluation](/docs/evaluation/core-concepts#batch-evaluation)."
- **Our assessment**: Batch evaluation is the retrospective/backfill complement
  to continuous scoring — run the same judge against selected past observations
  (e.g., to re-score a population after a rubric change). It pairs with the
  dataset-sourcing workflow in #196 (batch-adding observations to datasets). This
  gives teams both an always-on surface and an on-demand historical surface with
  one evaluator definition.

### Claim 6: A documented troubleshooting path addresses "why is my observation-level evaluator not executing?" — a rule/observation-scope mismatch footgun
- **Evidence**: The page's inline link to the FAQ entry `observation-eval-not-executing`.
- **Confidence**: emerging
- **Quote**: "_[Why is my observation-level evaluator not executing?](/faq/all/observation-eval-not-executing)_"
- **Our assessment**: The page links out to a troubleshooting FAQ for a common
  failure — an observation-level evaluator not firing. This flags a documented
  footgun in the rule/observation-scope model (an evaluator attached at the wrong
  level, or a rule that doesn't match the observations it was expected to score).
  The linked FAQ page is a candidate for future extraction; here it's recorded as
  evidence that this operational failure mode exists and is vendor-documented.

### Claim 7: Other ways to score live traffic beyond automated evaluators are Scores via UI / annotation queues, user feedback, and Scores via API/SDK — a menu Langfuse presents as alternatives to continuous automated scoring
- **Evidence**: The "Other ways to score live traffic" table, listing the
  alternative methods and their use.
- **Confidence**: settled
- **Quote**: "Review a sample of traces manually — [Scores via UI](/docs/evaluation/evaluation-methods/scores-via-ui), [annotation queues](/docs/evaluation/evaluation-methods/annotation-queues)"
- **Our assessment**: This restates the five-method taxonomy already captured in
  #195 (Claim 4) — the offline/online methods menu. Per the triage guidance, this
  was flagged as overlap and is noted rather than re-extracted; the table's value
  here is confirming that Langfuse frames annotation queues, user feedback, and
  API/SDK scores as the manual/alternative tier beneath automated online scoring.

### Claim 8: The manual setup path treats the evaluator as a reusable artifact — you create it and can save it, then either create a rule from the filters you used while testing or attach it to an existing rule
- **Evidence**: The "Attach a rule" step's two options for wiring the saved
  evaluator to a rule.
- **Confidence**: emerging
- **Quote**: "After you save the evaluator, create a rule from the filters you used while testing, or attach the evaluator to an existing rule."
- **Our assessment**: Reinforces Claim 3's test-then-attach flow: the evaluator is
  authored once, validated, and then bound to a rule either fresh (reusing the
  test filters) or by joining an existing rule. This "reuse the filters you
  validated against" shortcut blurs the boundary between the validation set and
  the live-scoring set — worth noting as a subtlety: the production rule inherits
  exactly the filter you tested on, keeping validation and live scope consistent.

### Claim 9: Online evaluation can be set up agentically — via the Langfuse Agent Skill (or Cursor plugin which includes it) by prompting a coding agent, or by installing the skill via the npm skills CLI
- **Evidence**: The "Agentic installation" section with three paths (ask the
  coding agent, Cursor plugin, npm `skills` CLI install).
- **Confidence**: settled
- **Quote**: "Install the [Langfuse Agent Skill](https://github.com/langfuse/skills) to let your coding agent access all Langfuse features."
- **Our assessment**: This is the online-eval page's agentic-setup entry point,
  echoing the install surface already documented in `docs-langfuse-agent-skill.md`
  (#1056, Claims 5–7: `npx skills add langfuse/skills --skill "langfuse"`, Cursor
  plugin, manual clone+symlink). The page frames "Set up online evaluation for
  this application with Langfuse." as a one-line agent prompt. Overlap with #1056
  is noted, not re-extracted.

## Concrete Artifacts

### Agentic install — skills CLI (verbatim bash, "Agentic installation" section)
```bash
npx skills add langfuse/skills --skill "langfuse"
```
Per-agent targeting:
```bash
npx skills add langfuse/skills --skill "langfuse" --agent "<agent-id>"
```

### Rule definition (verbatim prose, "Attach a rule to incoming traces" step)
> "A rule defines **which** incoming observations are scored: filters, sampling
> rate, and one or more evaluators. Review the matching volume from the past
> seven days. For LLM-as-a-Judge, also review the estimated cost and lower the
> sampling rate if needed."

### Other ways to score live traffic (verbatim table, "Other ways to score live traffic")
```
If you want to...                               Use
Review a sample of traces manually              Scores via UI, annotation queues
Capture thumbs-up/down or other feedback        User feedback
signals from users
Push scores from your own pipeline or agent     Scores via API/SDK
```

## Cross-References

- **Corroborates**:
  - `docs-langfuse-evaluation-core-concepts.md` (#195) **Claim 11** (online
    evaluation auto-scores production traces; catch issues immediately) and
    **Claim 6** (observation-level online eval for production scaling). This page
    is the operational how-to behind those concepts: the Rule mechanism (Claim 1
    here) is the concrete scoping primitive that makes observation-level online
    scoring (Claim 6 there) deployable, and the "scores as they arrive" step
    (Claim 4 here) instantiates the auto-scoring Loop (Claim 11 there). Directionally
    aligned — this page deepens, does not oppose, #195.
  - `docs-langfuse-datasets.md` (#196) **Claim 3** (batch-add observations to
    datasets from the Observations table). Batch evaluation here (Claim 5) is a
    sibling batch operation over the same historical-observation surface — both
    run retrospective jobs against selected production observations. Same
    Workflow batch-over-observations model, different output (scores vs dataset
    items).
  - `docs-langfuse-agent-skill.md` (#1056) **Claims 5, 7** (the `npx skills add
    langfuse/skills --skill "langfuse"` install and the Cursor plugin /
    agent-instruction distribution). This page's agentic-install section (Claim 9
    here, and the skills CLI artifacts) reuses exactly those install mechanics to
    stand up online evaluation. No new info beyond #1056; noted as overlap.
  - `docs-google-sre-prodcast-01-03-alerting.md` (per triage, tangential —
    curated-SLI discipline) — online eval here, and the Alerts follow-up (#1069),
    are concrete implementations of the "alert/measure on curated signals, not raw
    anomalies" discipline: the 7-day-volume + cost preview (Claim 2) is a curation
    gate before a signal goes live. Directionally aligned, not directly cited to a
    specific claim number.

- **Contradicts**: None. This page agrees with and operationalizes #195; no claim
  here opposes any existing source note. No contradiction issue filed.

- **Extends**:
  - `docs-langfuse-evaluation-core-concepts.md` (#195) — supplies the rollout and
    governance mechanics #195 intentionally abstracted away: the Rule primitive
    (Claim 1), the sampling-rate cost lever for LLM-as-a-Judge (Claim 2), the
    test-before-attach loop (Claim 3), and batch evaluation (Claim 5). #195 is the
    conceptual model; this page is the deployment procedure.
  - `docs-langfuse-alerts.md` (#1069) **Claim 1** (scores as alertable signals;
    boolean-score-average rate alerts). This page's "watch the metric over time"
    step (Claim 4) is the monitoring input that #1069's alerts then make actionable
    ("Set an alert when a score drops below a threshold" is a Next-steps link from
    this page). Together they form closed-loop eval observability: score → dashboard
    → alert.

- **Novel** (first appearances in the corpus):
  - The **Rule primitive** with its three-part definition (filters + sampling rate
    + one-or-more evaluators) as the concrete production-scoring deployment
    mechanism (Claim 1). #195 described observation-level online eval as a pattern
    but not the Rule object that configures it.
  - The **sampling-rate as cost-control-dial** pattern for always-on
    LLM-as-a-Judge, with the pre-enable 7-day-volume + estimated-cost review
    (Claim 2). This is the corpus's first concrete cost-governance lever for
    running a judge continuously in production.
  - The **test-the-judge-first-before-attach** production-validation loop (Claim 3,
    8).

## Guide Impact

- **Chapter 05 (LLM Ops Reliability — eval harness material)**: Extend #195's
  existing online-eval guidance with the operational rollout mechanics this page
  adds:
  - Add the **Rule primitive** (Claim 1) as the recommended production
    configuration object for binding evaluators to a filtered, sampled observation
    stream — the deployment-time scoping control for always-on scoring.
  - Add **sampling-rate cost governance** for LLM-as-a-Judge (Claim 2): before
    enabling an online judge, review matching volume from the past seven days and
    estimated cost, and use the sampling rate as the primary cost dial. This is the
    concrete operationalization of #195's "scope the judge to observation level to
    cut volume/cost."
  - Add the **test-before-attach rollout** (Claim 3, 8): create evaluator → test
    and iterate on representative sample observations → then attach a rule, so a
    judge is validated against real traffic before it scores live. Frame as
    validation-before-live-exposure, the eval-harness analogue of staging.
  - Add **batch evaluation** (Claim 5) as the complementary retrospective surface
    for re-scoring historical observations alongside continuous scoring.

- **Chapter 02 (Observability — eval scores as monitorable signals)**: Add the
  score-on-arrival + dashboard-monitoring step (Claim 4) as the concrete way online
  scores become monitorable time-series signals (with the judge's reasoning
  attached), and pair it with the alerting follow-up from #1069 (score → dashboard
  → alert) to present a complete score-observability pipeline.

## Extraction Notes

- Source fetched 2026-09-03 via WebFetch (Markdown rendering of the docs page,
  fully public — the page serves plain Markdown per its stated convention; a
  trailing "Agent Instructions" boilerplate block is appended to every Langfuse
  docs page and was used only as incidental context, not extracted).
- Per the triage guidance, extraction was kept **tight to the rule/sampling/cost
  rollout mechanics** and did not re-extract the offline/online loop, Score data
  model, five-method taxonomy, or judge-prompt structure — those are already in
  #195. The "Other ways to score live traffic" menu (the five-method taxonomy in
  compact form, Claim 7) is noted as overlap with #195 Claim 4 and flagged, not
  re-extracted.
- **Contradiction check**: Re-read #195 (Claims 1, 6, 11), #1056 (Claims 5, 7),
  #196 (Claim 3), and #1069 (Claim 1) before writing cross-references. No claim
  number was invented; each cited claim was located and matches the content cited
  (§4b). No contradiction with any existing note — this page operationalizes
  #195's concepts rather than opposing them. No contradiction issue filed.
- **Candidates from `miner-related-notes.md` processed (cite or dismiss each):**
  - `docs-langfuse-evaluation-core-concepts.md` — **Cited** (Corroborates
    Claims 6/11; Extends — the primary overlap; this is an extension note per the
    triage).
  - `docs-langfuse-agent-skill.md` — **Cited** (Corroborates Claims 5/7 — the
    agentic-install path reuses its install mechanics).
  - `docs-langfuse-datasets.md` — **Cited** (Corroborates Claim 3 — batch over
    observations parallels batch evaluation).
  - `docs-langfuse-mcp-server.md` — **Dismissed**. MCP server surface for coding
    agents; unrelated to the eval rule/sampling/cost mechanics.
  - `docs-langfuse-security-and-guardrails.md` — **Dismissed**. Guardrail-scanner
    pipeline (PII anonymization, scanner composition); no eval-rollout content.
  - `docs-langfuse-roadmap.md` — **Dismissed**. Roadmap of planned strategy; no
    shipped online-eval rollout mechanics to compare.
  - `docs-langfuse-sdk-overview.md` — **Dismissed**. SDK instrumentation methods /
    OTel mapping; no Rule or sampling-cost content.
  - `docs-langfuse-glossary.md` — **Dismissed**. Telemetry data model
    (traces/observations/scores); no online-eval rollout mechanics.
  - `docs-google-sre-prodcast-04-05-furino-slos.md` — **Dismissed**. SLO
    construction/SLI theory with Sal Furino; no eval-rollout overlap beyond the
    curated-SLI thread already covered by the alerting note.
  - `blog-litellm-auto-router-v2.md` — **Dismissed**. Model-routing config; no
    online-eval rule/sampling content.
- **Additional manual search of `source-notes/`:** `docs-langfuse-alerts.md`
  (#1069) **Cited** (Extends — the score-drop-alert follow-up this page links to).
  Other Langfuse sibling notes (prompt-management, cli, compatibility,
  metrics-overview, mcp-server) were checked and **dismissed** — no Rule /
  sampling-cost / online-eval-rollout claims.
- **Troubleshooting gap**: The page links "Why is my observation-level evaluator
  not executing?" to an FAQ page (Claim 6). That FAQ entry is a candidate for
  future extraction — this note records only that the footgun exists and is
  vendor-documented, not the FAQ's full content.
- `confidence_overall` is set to **emerging**, consistent with the sibling Langfuse
  evaluation notes (#195): the Rule/sampling mechanics are authoritative vendor
  product documentation (the individual mechanics claims grade `settled`), but
  their long-term operational value to practitioners is an interpretation, and the
  page is living docs, so the aggregate is `emerging` rather than `settled`.
- No part of the source was paywalled; the page is fully public.

