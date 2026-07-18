# Model routing (MVP)

Agent workflows use `anthropics/claude-code-action` (and the Claude Code CLI)
routed to **DeepSeek's Anthropic-compatible API** via
`.github/actions/configure-deepseek`.

```text
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY = DEEPSEEK_API_KEY
```

`CLAUDE_CODE_OAUTH_TOKEN` is **not** required for the MVP path.

## Worker → model map (wired)

| Worker | Model | Notes |
|--------|-------|-------|
| Pre-screen / Prospector / Scribe / Site-crawl | `deepseek-v4-flash` | Volume / cheap triage |
| **Miner** | `deepseek-v4-flash` | Direct DeepSeek API; off-peak cron only (see below) |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier review & synthesis |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `OPENROUTER_API_KEY` | **Optional** — only for Hy3 smoke / `miner-hy3-eval.yml` fallback |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Peak / valley pricing (DeepSeek V4)

DeepSeek may bill **2×** during peak windows (UTC **01:00–04:00** and
**06:00–10:00**). Scheduled LLM jobs avoid those hours:

| Workflow | Cron (UTC) |
|----------|------------|
| `miner-batch.yml` | `:19` at hours `0,4,5,10–23` |
| `daily-scan.yml` | `12:02` daily |
| `smith-on-source-merge.yml` | Sat `15:19`, Thu `00:02` |
| `gardener.yml` | Sun `14:02` (Python; Assayer follow-up stays off-peak) |
| `herald-weekly.yml` | Sun `16:02` |

Minutes are offset from `:00` to reduce top-of-hour Actions contention.
Event-driven jobs (pre-screen, Prospector, Assayer on PR labels) cannot
defer to off-peak without queueing; keep those prompts short.

## Hy3 note (historical)

Miner ran OpenRouter `tencent/hy3:free` through **2026-07-21** after a
golden-set replay scored 4/4 Assayer APPROVE (`docs/HY3-MINER-EVAL.md`).
Post-trial, production Miner uses **DeepSeek V4 Flash** (price + single
auth stack). Keep `configure-openrouter-hy3` + eval workflows if a
quality regression needs a paid-Hy3 A/B.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing auth/routing.
It should print `hitchhiker smoke test ok` via DeepSeek.

## Cost targets (MVP)

- Bootstrap (~50–100 notes): DeepSeek Flash (triage + Miner) + DeepSeek Pro Assayer/Smith
- Prefer off-peak scheduled runs; watch Assayer REJECT rate after Miner→Flash
- Steady hybrid month after MVP: roughly **$50–150** (estimate)

Treat these as estimates.
