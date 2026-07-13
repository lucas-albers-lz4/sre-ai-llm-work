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
| #1 | [#21](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/21) | APPROVE | 0 (10/10 spot-checked) | 20 claims vs 17 baseline; +3 new claims |
| #2 | [#22](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/22) | APPROVE | 0 (5/5 spot-checked) | Corroborates all 12 baseline claims; +Claim 13, full YAML artifact |
| #3 | [#23](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/23) | APPROVE | 0 (5/16 spot-checked) | Author bio quote from RSC/JSON-LD — documented, not fabricated |
| #4 | [#24](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/24) | APPROVE | 0 (6/6 spot-checked) | 17 claims; comprehensive long-form extraction |

**Result: 4/4 APPROVE on first pass, 0 quote fabrication failures.**

## Decision

- **Switch Miner to Hy3** until 2026-07-21 if ≥3/4 APPROVE on first pass, 0 quote failures.
- **Stay on DeepSeek Pro** if repeated REJECT / quote fabrication.

**Recommendation (2026-07-13):** Criteria met — switch `miner-batch.yml` to OpenRouter Hy3 (`tencent/hy3:free`) for production Miner runs through 2026-07-21, then re-evaluate cost/quality vs DeepSeek Pro.

Eval PRs can be closed after scoring; delete `*-hy3-eval.md` files from main if any were merged by mistake (they should not be).
