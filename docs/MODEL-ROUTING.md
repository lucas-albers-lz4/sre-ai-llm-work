# Model routing (MVP)

Agent workflows use `anthropics/claude-code-action` (and the Claude Code CLI)
routed to **DeepSeek's Anthropic-compatible API** via
`.github/actions/configure-deepseek`. OpenRouter / Zen Messages peak-fill
wiring remains in `miner-batch.yml` for **manual trials** only. Zen free
chat-completions live drains use **`miner-zen-free-batch.yml`** (OpenCode
Action).

**2026-07-27 (#571):** Peak premise died — `deepseek-v4-flash-free` extracted
successfully on N=3 peak + N=3 off-peak golden #1. **Peak cron enabled** on
`miner-zen-free-batch.yml` (`:19` at UTC `1-3,6-9`) with default
`deepseek-v4-flash-free`. Off-peak Miner stays on paid DeepSeek Flash via
`miner-batch.yml`. Qwen3.5-plus parked (cost). Big Pickle is an alternate free
candidate (see `MINER-CANDIDATE-EVAL.md`). GPT-5 Nano out of scope.

```text
# Default (DeepSeek)
ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY = DEEPSEEK_API_KEY

# Manual OpenRouter Miner trial only
ANTHROPIC_BASE_URL=https://openrouter.ai/api
ANTHROPIC_AUTH_TOKEN = OPENROUTER_API_KEY

# Manual OpenCode Zen Miner trial (Messages / paid)
# Zen auths via x-api-key → ANTHROPIC_API_KEY; AUTH_TOKEN must be empty.
# Base URL is /zen (Claude Code appends /v1/messages).
ANTHROPIC_BASE_URL=https://opencode.ai/zen
ANTHROPIC_API_KEY = OPENCODE_ZEN_API_KEY
```

`CLAUDE_CODE_OAUTH_TOKEN` is **not** required for the MVP path.

## Worker → model map (wired)

| Worker | Model | Notes |
|--------|-------|-------|
| Pre-screen / Prospector / Scribe / Site-crawl | `deepseek-v4-flash` | Volume / cheap triage |
| **Miner** | `deepseek-v4-flash` | Direct DeepSeek API; off-peak cron `0,4,5,10–23` UTC |
| **Miner peak-fill** | `deepseek-v4-flash-free` | Zen free via `miner-zen-free-batch.yml` cron `:19` at UTC `1-3,6-9` (#571/#606). Validated alternate: `big-pickle` (manual `miner-zen-free-batch.yml` only; live APPROVE #611). |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier review & synthesis |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `OPENROUTER_API_KEY` | Optional — manual Miner OpenRouter trials / Hy3 / Nemotron smoke |
| `OPENCODE_ZEN_API_KEY` | **Required for peak-fill** — `miner-zen-free-batch.yml` schedule + manual Zen free / `backend=zen` |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Peak / valley pricing (DeepSeek V4)

DeepSeek may bill **2×** during peak windows (UTC **01:00–04:00** and
**06:00–10:00**). Off-peak Miner uses paid Flash on the direct API; peak
uses Zen **free** Flash-free (no 2× surcharge; #571 confirmed extractions
work in-window):

| Workflow | Cron (UTC) | Backend |
|----------|------------|---------|
| `miner-batch.yml` | `:19` at hours `0,4,5,10–23` | DeepSeek Flash (paid) |
| `miner-zen-free-batch.yml` | `:19` at hours `1-3,6-9` | Zen free `deepseek-v4-flash-free` |
| `daily-scan.yml` | `12:02` daily | DeepSeek Flash |
| `smith-on-source-merge.yml` | Sat `15:19`, Thu `00:02` | DeepSeek Pro |
| `gardener.yml` | Sun `14:02` (Python; Assayer follow-up stays off-peak) | — |
| `herald-weekly.yml` | Sun `16:02` | DeepSeek Pro |

Minutes are offset from `:00` to reduce top-of-hour Actions contention.
Manual runs: `gh workflow run miner-batch.yml -f backend=flash` (default);
`gh workflow run miner-zen-free-batch.yml -f model=deepseek-v4-flash-free`.

Event-driven jobs (pre-screen, Prospector, Assayer on PR labels) cannot
defer to off-peak without queueing; keep those prompts short.

## Peak-fill status (enabled 2026-07-27)

**2026-07-23:** OpenRouter Nemotron free failed real Miner batches (Claude Code
gateway errors). Peak cron removed from `miner-batch.yml`.

**2026-07-26:** Zen free `deepseek-v4-flash-free` cleared golden + live Assayer
(#564 / PR #569) via `miner-zen-free-batch.yml`.

**2026-07-27 (#571):** Peak premise (free DeepSeek deprioritized in DeepSeek
peak windows) **died** — N=3 peak + N=3 off-peak golden #1 all extracted.
Peak cron enabled on `miner-zen-free-batch.yml`. Fail-closed junk-PR + one
no-op retry shipped in #572. `$/note` for zen-free peak = **$0** (Zen free
tier); off-peak paid Flash remains the cost floor for scheduled Miner.

```bash
gh workflow run miner-zen-free-smoke.yml -f model=deepseek-v4-flash-free
gh workflow run miner-zen-free-eval.yml -f model=deepseek-v4-flash-free -f issue_number=1
gh workflow run miner-zen-free-batch.yml -f model=deepseek-v4-flash-free
gh workflow run miner-zen-free-batch.yml -f model=big-pickle   # alternate free
```

Requires `OPENCODE_ZEN_API_KEY` for zen-free schedule. Zen `/v1/messages` for
Claude Code (qwen3.5/3.6/3.7 plus/max, claude-*) remains manual only.

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
- Off-peak paid Flash; peak Zen free Flash-free (`$/note` ≈ $0 on free tier)
- Steady hybrid month after MVP: roughly **$50–150** (estimate)

Treat these as estimates.

