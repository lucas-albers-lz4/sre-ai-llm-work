---
source_url: https://github.github.com/gh-aw/blog/2026-06-08-migrating-from-effective-tokens-to-ai-credits/
source_type: blog-post
title: "Effective Tokens replaced by AI Credits (GitHub Agentic Workflows)"
author: GitHub Agentic Workflows team (gh-aw)
date_published: 2026-06-08
date_extracted: 2026-06-08
last_checked: 2026-06-08
status: current
confidence_overall: settled
issue: "#1113"
---

# Effective Tokens replaced by AI Credits (GitHub Agentic Workflows)

> Breaking change announcement: AI Credits (AIC, 1 AIC = $0.01 USD) replaces
> Effective Tokens (ET) as the primary spend metric in gh-aw, with ET demoted to
> a legacy compatibility field — practitioners with ET-based dashboards and guardrails
> must migrate and can use `gh aw fix --write` for automated updates.

## Source Context

- **Type**: blog-post (official GitHub Agentic Workflows blog — the same team behind
  the `gh aw` CLI, the Agent Factory series, and the normative Effective Tokens
  specification. Published 2026-06-08, the same day as extraction. Short-form
  announcement post covering a breaking metric change, not a long conceptual piece.)
- **Author credibility**: First-party from the GitHub Agentic Workflows team (Don Syme,
  Peli de Halleux, Mara Kiefer — GitHub Next / Microsoft Research). This is the
  authoritative source for platform behavior changes. The announcement supersedes the
  April 2026 Effective Tokens specification (`docs-ghaw-effective-tokens-specification.md`)
  as of this date.
- **Scope**: Covers the metric change itself (ET → AIC), practical impact on `gh aw audit`
  and `gh aw logs`, the migration command, and a brief metric reference table. Does NOT
  cover: the full AIC formula or token weights, whether the Copilot Multiplier is preserved
  in AIC computation, detailed migration steps beyond `gh aw fix --write`, AIC guardrail
  syntax (if any), or a deprecation timeline for ET (no removal date stated). The "Where
  to read more" section links to four documentation resources that were not individually
  followed during this extraction.

## Extracted Claims

### Claim 1: Effective Tokens (ET) have been replaced by AI Credits (AIC) as the primary spend metric in the latest gh-aw build

- **Evidence**: Direct announcement statement in the post's opening section ("Effective
  Tokens replaced by AI Credits"), confirmed across multiple fetch passes as the post's
  primary claim.
- **Confidence**: settled (first-party platform announcement from the team that owns the
  metric definition)
- **Quote**: "In the latest gh-aw build, Effective Tokens (ET) have been replaced by AI
  Credits (AIC) as the primary spend metric."
- **Our assessment**: This is the core claim. Combined with Claim 4 (ET demoted to legacy),
  this represents a complete reversal of the cost-metric primacy established in
  `docs-ghaw-effective-tokens-specification.md`. The ET spec (Claim 1 there) positioned ET
  as the answer to "how do you measure what a multi-invocation agentic run actually cost in
  compute terms?" — this announcement replaces that answer with a dollar-denominated one.
  See contradiction issue #1118.

### Claim 2: AIC is the default cost metric in all gh-aw output; ET is available only as a legacy compatibility field

- **Evidence**: Explicitly stated in the post's opening section. The distinction between
  "default" and "legacy compatibility" clarifies that ET has not been removed but is no
  longer the primary output.
- **Confidence**: settled (first-party announcement; the default/legacy distinction is
  normative platform behavior)
- **Quote**: "AIC is now the default cost metric in gh-aw output. ET remains available
  only as a legacy compatibility field."
- **Our assessment**: The phrase "legacy compatibility field" is precise: ET is preserved
  for backward compatibility with existing tooling that reads the field, not as a
  recommended metric going forward. Teams whose automation reads `effective_tokens` from
  `gh aw logs --json` output will continue to get values, but they are no longer the
  platform's primary cost signal. The `docs-ghaw-agentic-ops.md` Concrete Artifacts section
  documents `effective_tokens int` as "Cost-normalized tokens" in the audit schema — that
  field description is now outdated.

### Claim 3: The migration rationale is direct billing alignment — AIC tracks monetary cost rather than a normalized token proxy

- **Evidence**: Stated as the explicit motivation for the change in the opening section.
  The post connects the change to two upstream dependencies: GitHub Copilot billing and
  models.dev pricing.
- **Confidence**: settled (first-party statement of design intent)
- **Quote**: "This change reflects GitHub Copilot billing and models.dev pricing. It makes
  spend tracking directly aligned to monetary cost instead of a normalized token proxy."
- **Our assessment**: This inverts the design philosophy of the ET specification.
  `docs-ghaw-effective-tokens-specification.md` Claim 2 quotes Design Goal 6 verbatim:
  "Carries no dependency on billing or pricing systems." The ET spec was explicitly designed
  to be billing-independent so the metric would remain stable across price changes. AIC
  abandons that stability in favor of real dollar alignment. Whether this is a net
  improvement depends on the use case: for budget accountability, dollar alignment is
  clearer; for stable cross-model cost comparison over time, billing-independence was
  a feature. This is not a neutral clarification — it is a design philosophy shift.

### Claim 4: Effective Tokens are deprecated in documentation and should be treated as legacy compatibility output

- **Evidence**: Stated in the "What this means in practice" bullet list. Corroborated by
  the metric reference table which labels ET as "deprecated legacy metric."
- **Confidence**: settled (first-party deprecation statement)
- **Quote**: "Effective Tokens are deprecated in documentation and should be treated as
  legacy compatibility output."
- **Our assessment**: "Deprecated in documentation" means ET is no longer the prescribed
  metric in the gh-aw reference documentation — the specification note
  (`docs-ghaw-effective-tokens-specification.md`) should be considered superseded. However,
  no removal date is given, and the post says ET "remains available" — so existing ET-based
  tooling will not break immediately. Teams should plan migration but there is no stated
  deadline.

### Claim 5: `gh aw audit` and `gh aw logs` report AI Credits as the primary spend metric

- **Evidence**: First bullet point of the "What this means in practice" section. Directly
  names the two most commonly used cost-reporting commands.
- **Confidence**: settled (first-party description of CLI behavior in the current build)
- **Quote**: "`gh aw audit` and `gh aw logs` report AI Credits as the primary spend metric."
- **Our assessment**: These are the two observability commands that practitioners use for
  cost visibility. The `docs-ghaw-agentic-ops.md` Concrete Artifacts section (Audit Workflow
  Run Data Schema) includes `effective_tokens int` as a field — that schema is now secondary
  output. The AIC-equivalent field name in the output schema is not specified in this post;
  practitioners will need to check the updated `gh aw logs --json` schema or the linked
  documentation for the field name.

### Claim 6: Cost reporting and budget discussions should reference AIC values going forward

- **Evidence**: Third bullet point of the "What this means in practice" section. Normative
  guidance on practitioner behavior.
- **Confidence**: settled (first-party behavioral recommendation from the platform team)
- **Quote**: "Cost reporting and budget discussions should use AIC values."
- **Our assessment**: This is the operational implication for teams. Any dashboard,
  report, or alert threshold currently expressed in ET units needs a migration decision:
  either convert existing ET thresholds to AIC equivalents, or rebuild from scratch using
  the AIC metric. The `gh aw fix --write` command (Claim 7) handles this automatically
  for workflow configurations, but custom dashboards and external tooling require manual
  updates.

### Claim 7: AIC is the primary spend metric at a rate of 1 AIC = $0.01 USD

- **Evidence**: The "Metric reference" section provides a reference table with explicit
  pricing. This is the single most concrete technical detail in the post.
- **Confidence**: settled (first-party metric definition with explicit dollar value)
- **Quote**: "AI Credits (AIC): primary spend metric (1 AIC = $0.01 USD)"
- **Our assessment**: 1 AIC = $0.01 USD (1 cent) is a clean denomination. For context:
  100 AIC = $1.00. This is a direct dollar representation, not a normalized unit. Unlike
  ET, whose design explicitly avoided billing dependencies, AIC is explicitly a monetary
  unit — it will change in meaning if GitHub Copilot pricing changes (i.e., if the
  AIC-to-USD conversion rate changes). The current conversion rate (1:$0.01) should be
  treated as current-as-of-June-2026 and not assumed to be permanent. For Ch02: this
  pricing anchor should be cited with a "as of June 2026" qualifier.

### Claim 8: `gh aw fix --write` provides automated migration for repositories that need workflow updates

- **Evidence**: Named as the migration command in the "What this means in practice" section.
  The `--write` flag pattern is consistent with other gh-aw fix commands throughout the
  corpus.
- **Confidence**: settled (first-party command documented in the release announcement)
- **Quote**: (no direct quote wrapping the command; the command `gh aw fix --write` appears
  as a standalone code block in the source)
- **Our assessment**: The `--write` flag implies a dry-run default (running without
  `--write` presumably shows what would change). This is consistent with the gh-aw CLI
  conventions seen elsewhere in the corpus. For teams with many repositories using ET-based
  configurations, this command represents a low-effort migration path. The post does not
  specify what exactly `gh aw fix --write` modifies — presumably ET-based guardrail
  configurations and workflow frontmatter that references ET thresholds.

## Concrete Artifacts

### Migration command (from "What this means in practice" section)

```sh
# Automatically update workflow configurations from ET-based to AIC-based
gh aw fix --write
```

*Source: GitHub Agentic Workflows blog, 2026-06-08*

### Metric reference table (from "Metric reference" section)

```
Metric                      Status
--------------------------  ----------------------------
AI Credits (AIC)            primary spend metric (1 AIC = $0.01 USD)
Effective Tokens (ET)       deprecated legacy metric
```

*Source: GitHub Agentic Workflows blog, 2026-06-08*

### Post structure (full heading outline)

```
1. Effective Tokens replaced by AI Credits  [intro section]
2. What this means in practice              [bullet list + migration command]
3. Metric reference                         [metric reference table]
4. Where to read more                       [links to 4 documentation resources]
```

## Cross-References

- **Contradicts**: `docs-ghaw-effective-tokens-specification.md` — see contradiction
  issue **#1118**. The ET spec (Claim 1, Claim 2) describes ET as the normative primary
  cost metric with explicit billing-independence as a design goal (Goal 6: "Carries no
  dependency on billing or pricing systems"). This post supersedes that claim: AIC is now
  primary, and it is explicitly billing-aligned (1 AIC = $0.01 USD). The design philosophy
  shifts from "stable normalized compute intensity" to "direct dollar cost." Recommended
  verdict: `superseded` (the AIC post is 2 months newer than the ET spec and explicitly
  announces a platform change by the same team).

- **Extends**:
  - `docs-ghaw-agentic-ops.md` Concrete Artifacts → Audit Workflow Run Data Schema section:
    The `effective_tokens int` ("Cost-normalized tokens") field in `gh aw logs --json`
    output is now a legacy field. The AIC-equivalent field name is not stated in this post
    but will appear in the updated schema. The Agentic Ops workflows that currently trigger
    on ET thresholds (Claim 3 of that note) will need migration via `gh aw fix --write`.
  - `blog-ghaw-weekly-2026-06-01.md` Claim 4: Per-workflow 24-hour effective-token
    guardrails (introduced in v0.77.4, May 31, 2026) used ET shorthand syntax. These
    guardrails are based on the now-deprecated ET metric. Whether AIC-based guardrails
    replace them, or whether `gh aw fix --write` updates guardrail syntax from ET to AIC
    units, is not specified in this post — see Claim 8 note.
  - `blog-ghaw-agent-observability.md` Claim 4 (Portfolio Analyst pattern: "some agents
    were way too chatty with their LLM calls"): The Portfolio Analyst's cost analysis was
    expressed in ET terms. With AIC as primary, a rebuilt Portfolio Analyst would use AIC
    values for the same analysis — the pattern is unchanged but the metric unit changes.

- **Corroborates**:
  - `blog-bswen-mcp-token-cost.md` (general cost-awareness theme): AIC's explicit
    dollar denomination ($0.01/AIC) reinforces the practical cost-tracking concern that
    Bswen's note documents for MCP token costs. Both sources agree that practitioners
    need concrete dollar-cost visibility, not just normalized units.

- **Novel** (what this note adds that no prior source covers):
  - **AIC as the new primary gh-aw spend metric**: No prior corpus source mentions AI
    Credits (AIC) as a gh-aw metric at all. This is the first definition in the corpus.
  - **1 AIC = $0.01 USD**: The explicit dollar-to-AIC conversion rate is new.
  - **ET deprecation announcement**: Prior notes treat ET as current and normative.
    This is the first corpus source to mark ET as deprecated.
  - **`gh aw fix --write` migration command**: Not mentioned in any prior corpus note.
  - **Design philosophy shift from billing-independence to billing-alignment**: The ET
    spec explicitly rejected billing dependency; this post embraces it. This is a
    substantive architectural change to how gh-aw communicates cost.

## Guide Impact

- **Chapter 02 (Foundations — LLM Cost Measurement)**: If the guide currently recommends
  ET as the normative gh-aw cost metric (based on `docs-ghaw-effective-tokens-specification.md`),
  update to recommend AIC instead. Cite AIC as 1 AIC = $0.01 USD (as of June 2026). Note
  ET as the prior metric, now legacy. Acknowledge the design philosophy shift: AIC trades
  ET's billing-independence for direct dollar clarity. Do not present ET and AIC as
  equivalent alternatives — the platform has chosen AIC as primary.

- **Chapter 04 (Multi-Agent Patterns — Cost Attribution)**: Any ET-based cost attribution
  guidance (e.g., ET_total for comparing fan-out strategies, per-invocation ET from the
  execution graph) should be updated to use AIC. The normalized cross-model cost model
  that ET provided (via Copilot Multiplier and token class weights) may no longer be
  directly accessible in primary output — whether AIC preserves the same normalization
  mechanics is not stated in this post.

- **Chapter 05 (Team Adoption — Cost Tracking)**: Add migration guidance:
  (1) run `gh aw fix --write` for automated workflow updates;
  (2) update ET-based dashboards to read AIC fields from `gh aw audit` and `gh aw logs`;
  (3) treat existing ET guardrail thresholds as requiring re-expression in AIC units
  (convert: N ET → M AIC is not specified in this post, so manual recalibration may be
  needed);
  (4) note that AIC is dollar-denominated and may change in meaning if Copilot pricing
  changes (ET did not have this risk).

## Extraction Notes

1. **Source accessed via WebFetch AI-processing**: The WebFetch tool processes page
   content through an AI model before returning results. Three separate fetch passes
   were made with different prompts (overview, verbatim full text, heading-by-heading).
   Quotes in the "Extracted Claims" section are reproduced from the second and third
   fetch passes, which consistently returned the same phrasing across passes. The post
   is short (four sections) and the quoted passages were returned consistently. However,
   as with all WebFetch-extracted quotes, exact character-for-character fidelity to the
   source HTML cannot be guaranteed — the Assayer should spot-check against the live URL.

2. **"Where to read more" links not followed**: The post's final section links to four
   documentation resources (described as covering Cost Management, `gh aw audit`,
   AI Credits specifications, and related content). These URLs were not individually
   returned by WebFetch. They were not followed as linked pages because the post's
   primary claims are self-contained; the linked docs are reference material, not
   additional claims. If the Smith needs the AIC formula or field schema, those linked
   docs should be mined separately.

3. **AIC computation formula not in scope**: This post announces the metric change but
   does not describe the AIC computation formula (whether it uses the same ET token
   class weights and Copilot Multiplier, or a different calculation). The "where to read
   more" links likely lead to an AIC specification document analogous to the ET spec.
   That document should be sourced separately for full formula details.

4. **No deprecation timeline for ET**: The post says ET "remains available" as a legacy
   field but gives no removal date. Teams relying on ET can continue to use it for now,
   but the platform's direction is clear.

5. **Contradiction issue #1118 filed**: Before opening this PR, a contradiction issue
   was filed against `docs-ghaw-effective-tokens-specification.md` with recommended
   verdict `superseded`. See §Cross-References above.
