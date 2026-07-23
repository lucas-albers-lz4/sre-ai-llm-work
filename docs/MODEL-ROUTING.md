# Model routing (MVP)

Agent workflows use `anthropics/claude-code-action` (and the Claude Code CLI)
routed to **DeepSeek's Anthropic-compatible API** via
`.github/actions/configure-deepseek`. OpenRouter peak-fill wiring remains in
`miner-batch.yml` / `configure-openrouter-hy3` but the **peak cron is
disabled** until a free model proves agent-reliable under Miner tool use.

```text
# Default (DeepSeek)
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY = DEEPSEEK_API_KEY

# Manual OpenRouter Miner trial only (peak cron OFF)
ANTHROPIC_BASE_URL=https://openrouter.ai/api
ANTHROPIC_AUTH_TOKEN = OPENROUTER_API_KEY
```

`CLAUDE_CODE_OAUTH_TOKEN` is **not** required for the MVP path.

## Worker → model map (wired)

| Worker | Model | Notes |
|--------|-------|-------|
| Pre-screen / Prospector / Scribe / Site-crawl | `deepseek-v4-flash` | Volume / cheap triage |
| **Miner** | `deepseek-v4-flash` | Direct DeepSeek API; off-peak cron `0,4,5,10–23` UTC |
| **Miner peak-fill** | — | **Disabled** (2026-07-23). Nemotron Ultra free failed multi-turn Miner (empty/malformed HTTP 200). Manual `backend=nemotron` only for experiments |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier review & synthesis |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `OPENROUTER_API_KEY` | Optional — manual Miner OpenRouter trials / Hy3 / Nemotron smoke (not required while peak cron is off) |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Peak / valley pricing (DeepSeek V4)

DeepSeek may bill **2×** during peak windows (UTC **01:00–04:00** and
**06:00–10:00**). Scheduled LLM jobs avoid those hours:

| Workflow | Cron (UTC) | Backend |
|----------|------------|---------|
| `miner-batch.yml` | `:19` at hours `0,4,5,10–23` | DeepSeek Flash |
| `miner-batch.yml` peak-fill | *(disabled)* | was OpenRouter Nemotron free |
| `daily-scan.yml` | `12:02` daily | DeepSeek Flash |
| `smith-on-source-merge.yml` | Sat `15:19`, Thu `00:02` | DeepSeek Pro |
| `gardener.yml` | Sun `14:02` (Python; Assayer follow-up stays off-peak) | — |
| `herald-weekly.yml` | Sun `16:02` | DeepSeek Pro |

Minutes are offset from `:00` to reduce top-of-hour Actions contention.
Manual runs: `gh workflow run miner-batch.yml -f backend=flash` (default).
`backend=nemotron` is trial-only while peak cron is off.

Event-driven jobs (pre-screen, Prospector, Assayer on PR labels) cannot
defer to off-peak without queueing; keep those prompts short.

## Peak-fill status (disabled)

**2026-07-23:** OpenRouter `nvidia/nemotron-3-ultra-550b-a55b:free` passed
`nemotron-smoke-test.yml` (1-turn) but failed real Miner batches with Claude
Code errors such as empty/malformed HTTP 200 (“proxy/gateway”) and
unparseable provider bodies mid tool-use. Peak cron removed from
`miner-batch.yml`. Re-enable only after a free model completes a full
source-note extraction + Assayer path.

Smoke (when retrying a candidate model):

```bash
gh workflow run nemotron-smoke-test.yml   # or a model-specific smoke
gh workflow run miner-batch.yml -f backend=nemotron  # single manual trial
```

## Hy3 note (historical)

Miner ran OpenRouter `tencent/hy3:free` through **2026-07-21** after a
golden-set replay scored 4/4 Assayer APPROVE (`docs/HY3-MINER-EVAL.md`).
Post-trial, production Miner used **DeepSeek V4 Flash** (price + single
auth stack) off-peak. Keep `configure-openrouter-hy3` + `miner-hy3-eval.yml`
for A/B if needed.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing DeepSeek
auth/routing. It should print `hitchhiker smoke test ok` via DeepSeek.

Dispatch `.github/workflows/nemotron-smoke-test.yml` only when validating
OpenRouter candidates (smoke ≠ Miner reliability).

## Cost targets (MVP)

- Bootstrap (~50–100 notes): DeepSeek Flash (triage + off-peak Miner) +
  DeepSeek Pro Assayer/Smith
- Prefer off-peak Flash; revisit free peak-fill after an agent-reliable model
- Steady hybrid month after MVP: roughly **$50–150** (estimate)

Treat these as estimates.
