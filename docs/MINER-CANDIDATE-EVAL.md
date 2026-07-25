# Miner candidate eval (cost reduction)

Miner-only program to find a cheaper (or free) model that matches current
**DeepSeek V4 Flash** Miner quality. Assayer / Smith / Herald /
contradiction stay on **DeepSeek V4 Pro**. Do not merge eval PRs.

Nemotron Ultra free failing on OpenRouter does **not** write off that
gateway — Hy3 free previously scored 4/4 Assayer APPROVE
([HY3-MINER-EVAL.md](HY3-MINER-EVAL.md)). Treat Nemotron as one bad model.

## Pass bar

Per candidate, run **sequentially** (fail fast):

```text
smoke (1-turn) → golden #1 → #2–#4 → live mining-queued trial (1 issue)
```

| Gate | Criterion |
|------|-----------|
| Smoke | `miner-candidate-smoke.yml` prints `miner candidate smoke test ok` |
| Golden | ≥3/4 Assayer APPROVE on issues #1–#4; 0 quote-fabrication fails |
| Live | One real `miner-batch` PR Assayer APPROVEs |
| Fail fast | Empty/malformed HTTP 200 mid tool-use, unparseable bodies, hard rate-limits |

Do **not** re-enable peak cron until smoke + golden + live all pass.

## Workflows

```bash
# Smoke
gh workflow run miner-candidate-smoke.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free
gh workflow run miner-candidate-smoke.yml \
  -f backend=zen -f model=qwen3.5-plus

# Golden-set eval (repeat issue_number=1..4)
gh workflow run miner-candidate-eval.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free -f issue_number=1

# Live queue trial
gh workflow run miner-batch.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free
gh workflow run miner-batch.yml \
  -f backend=zen -f model=qwen3.5-plus
```

Secrets: `OPENROUTER_API_KEY` (Wave A), `OPENCODE_ZEN_API_KEY` (Wave B).
Eval PRs: labels `miner-eval` + `source-note`; branch
`miner/eval-<slug>-issue-<N>-r<run_id>`; filename `*-<slug>-eval.md`.

Legacy one-offs (`nemotron-smoke-test.yml`, `opencode-zen-smoke-test.yml`,
`miner-hy3-eval.yml`) remain for history; prefer the parameterized workflows
above.

## Candidate ladder

Test **one model fully** before the next. Confirm free OpenRouter slugs in
the live catalog before each run (IDs churn).

### Wave A — OpenRouter free (coding-oriented)

Confirm slugs against the live OpenRouter catalog before each run (IDs churn).
As of 2026-07-25, `qwen/qwen3-coder:free` is **not** listed.

| # | Model | Smoke | #1 | #2 | #3 | #4 | Live | Notes / decision |
|---|-------|-------|----|----|----|----|------|------------------|
| 1 | `poolside/laguna-m.1:free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30164857692)) | running | | | | | |
| 2 | `poolside/laguna-xs-2.1:free` (or `laguna-s-2.1:free`) | | | | | | | |
| 3 | `cohere/north-mini-code:free` | | | | | | | |

Skip: `nvidia/nemotron-3-ultra-550b-a55b:free` (already failed multi-turn).

### Wave B — OpenCode Zen Messages (cheap paid)

Only `/v1/messages` models. Requires `OPENCODE_ZEN_API_KEY`.

| # | Model | Smoke | #1 | #2 | #3 | #4 | Live | Notes / decision |
|---|-------|-------|----|----|----|----|------|------------------|
| 1 | `qwen3.5-plus` | | | | | | | |
| 2 | `qwen3.7-plus` | | | | | | | |
| 3 | `claude-haiku-4.5` (fallback) | | | | | | | |

### Wave C — later

Zen free DeepSeek / MiniMax / Kimi need a chat-completions bridge — out of
scope until Waves A–B finish.

## Decision rules

| Outcome | Action |
|---------|--------|
| OpenRouter free clears bar + stable live | Prefer for peak-fill (optionally more Miner hours) |
| Zen Qwen Plus ≤ Flash cost at equal quality | Route peak (and/or more Miner) via Zen; Flash fallback |
| Free fails multi-turn; paid Zen wins | Zen for peak only; off-peak Flash |
| Nothing beats Flash | Stay on Flash; revisit when catalog changes |

## Golden set

| Issue | Baseline note |
|-------|---------------|
| #1 | `source-notes/blog-pagerduty-sre-agent-architecture.md` |
| #2 | `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` |
| #3 | `source-notes/blog-incidentio-ai-sre-incident-run.md` |
| #4 | `source-notes/blog-pagerduty-production-ai-agent-gaps.md` |
