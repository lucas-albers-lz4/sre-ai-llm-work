# Hy3 Miner eval (golden-set replay)

Compare **Tencent Hy3 (free)** on OpenRouter vs **DeepSeek V4 Pro** for Miner
extraction quality before switching production `miner-batch.yml`.

## Golden set (issues #1–#4)

| Issue | Baseline (DeepSeek) note |
|-------|--------------------------|
| #1 | `source-notes/blog-pagerduty-sre-agent-architecture.md` |
| #2 | `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` |
| #3 | `source-notes/blog-incidentio-ai-sre-incident-run.md` |
| #4 | `source-notes/blog-pagerduty-production-ai-agent-gaps.md` |

## Run eval

Actions → **Miner Hy3 Eval** → Run workflow → `issue_number`: `1` (repeat for 2–4).

Each run opens a PR labeled `miner-eval` + `source-note`. **Do not merge** eval PRs.

## Scorecard

| Issue | Hy3 PR | Assayer verdict | Quote failures | Notes |
|-------|--------|-----------------|----------------|-------|
| #1 | | | | |
| #2 | | | | |
| #3 | | | | |
| #4 | | | | |

## Decision

- **Switch Miner to Hy3** until 2026-07-21 if ≥3/4 APPROVE on first pass, 0 quote failures.
- **Stay on DeepSeek Pro** if repeated REJECT / quote fabrication.

Eval PRs can be closed after scoring; delete `*-hy3-eval.md` files from main if any were merged by mistake (they should not be).
