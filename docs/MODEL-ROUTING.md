# Model routing (MVP)

Agent workflows use `anthropics/claude-code-action` (and the Claude Code CLI)
routed to **DeepSeek's Anthropic-compatible API** via
`.github/actions/configure-deepseek`, except Miner **peak-fill** which uses
OpenRouter via `.github/actions/configure-openrouter-hy3`.

```text
# Default (DeepSeek)
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY = DEEPSEEK_API_KEY

# Miner peak-fill only (OpenRouter)
ANTHROPIC_BASE_URL=https://openrouter.ai/api
ANTHROPIC_AUTH_TOKEN = OPENROUTER_API_KEY
```

`CLAUDE_CODE_OAUTH_TOKEN` is **not** required for the MVP path.

## Worker → model map (wired)

| Worker | Model | Notes |
|--------|-------|-------|
| Pre-screen / Prospector / Scribe / Site-crawl | `deepseek-v4-flash` | Volume / cheap triage |
| **Miner (off-peak)** | `deepseek-v4-flash` | Direct DeepSeek API; cron hours `0,4,5,10–23` UTC |
| **Miner (peak-fill)** | `nvidia/nemotron-3-ultra-550b-a55b:free` | OpenRouter; cron hours `1–3,6–9` UTC (DeepSeek surge windows) |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier review & synthesis |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `OPENROUTER_API_KEY` | **Required for Miner peak-fill** (+ optional Hy3 / Nemotron smoke) |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Peak / valley pricing (DeepSeek V4)

DeepSeek may bill **2×** during peak windows (UTC **01:00–04:00** and
**06:00–10:00**). Scheduled LLM jobs avoid paying that surcharge:

| Workflow | Cron (UTC) | Backend |
|----------|------------|---------|
| `miner-batch.yml` (Flash) | `:19` at hours `0,4,5,10–23` | DeepSeek Flash |
| `miner-batch.yml` (peak-fill) | `:19` at hours `1–3,6–9` | OpenRouter Nemotron free |
| `daily-scan.yml` | `12:02` daily | DeepSeek Flash |
| `smith-on-source-merge.yml` | Sat `15:19`, Thu `00:02` | DeepSeek Pro |
| `gardener.yml` | Sun `14:02` (Python; Assayer follow-up stays off-peak) | — |
| `herald-weekly.yml` | Sun `16:02` | DeepSeek Pro |

Minutes are offset from `:00` to reduce top-of-hour Actions contention.
Both Miner crons share concurrency group `miner-batch` (no overlap).
Manual runs: `gh workflow run miner-batch.yml -f backend=flash|nemotron`.

Event-driven jobs (pre-screen, Prospector, Assayer on PR labels) cannot
defer to off-peak without queueing; keep those prompts short.

## Peak-fill validation path

Peak-fill is a **production cost hedge**, not a golden-set gate. Watch Assayer
APPROVE / quote-reject rate on PRs whose issue comments say
`Miner PR opened (nemotron)`. If quality holds, a later cutover can make
Nemotron the default Miner backend (still keeping Assayer/Smith on Pro).

Smoke before relying on cron:

```bash
gh workflow run nemotron-smoke-test.yml
```

## Hy3 note (historical)

Miner ran OpenRouter `tencent/hy3:free` through **2026-07-21** after a
golden-set replay scored 4/4 Assayer APPROVE (`docs/HY3-MINER-EVAL.md`).
Post-trial, production Miner used **DeepSeek V4 Flash** (price + single
auth stack) off-peak. Peak-fill now reuses OpenRouter with Nemotron free.
Keep `configure-openrouter-hy3` + `miner-hy3-eval.yml` for A/B if needed.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing DeepSeek
auth/routing. It should print `hitchhiker smoke test ok` via DeepSeek.

Dispatch `.github/workflows/nemotron-smoke-test.yml` after changing OpenRouter
peak-fill routing. It should print `nemotron smoke test ok`.

## Cost targets (MVP)

- Bootstrap (~50–100 notes): DeepSeek Flash (triage + off-peak Miner) +
  free Nemotron peak-fill + DeepSeek Pro Assayer/Smith
- Prefer off-peak Flash + peak-fill free; watch Assayer REJECT rate on
  `nemotron` Miner PRs
- Steady hybrid month after MVP: roughly **$50–150** (estimate); peak-fill
  should cut Flash Miner spend during former idle surge hours

Treat these as estimates.
