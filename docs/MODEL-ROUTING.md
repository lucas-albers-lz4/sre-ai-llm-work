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
| **Miner** | `tencent/hy3:free` (OpenRouter) | Trial through **2026-07-21** — golden-set 4/4 APPROVE; see `docs/HY3-MINER-EVAL.md` |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier review & synthesis |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `OPENROUTER_API_KEY` | **Required for Miner** — OpenRouter Hy3 (`tencent/hy3:free`) via `.github/actions/configure-openrouter-hy3` |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Hy3 note

Miner production path is **OpenRouter Hy3 free** (`tencent/hy3:free`) through
**2026-07-21**, after golden-set replay scored 4/4 Assayer APPROVE with 0 quote
failures (`docs/HY3-MINER-EVAL.md`). Assayer and other heavy workers stay on
DeepSeek V4 Pro. Re-evaluate cost/quality on or before 2026-07-21 and either
keep Hy3 or flip `miner-batch.yml` back to `configure-deepseek` +
`deepseek-v4-pro[1m]`.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing auth/routing.
It should print `hitchhiker smoke test ok` via DeepSeek.

## Cost targets (MVP)

- Bootstrap (~50–100 notes): DeepSeek Flash (triage) + Hy3 free Miner + DeepSeek Pro Assayer/Smith
- Hy3 free Miner trial (through 2026-07-21): lower Miner cash cost; watch OpenRouter free-tier rate limits
- Without Hy3 free: roughly **$200–500**
- Steady hybrid month after MVP: roughly **$50–150**

Treat these as estimates.
