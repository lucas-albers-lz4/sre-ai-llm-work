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
| Miner / Assayer / Smith / Herald / Contradiction | `deepseek-v4-pro[1m]` | Heavier extraction & review |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `OPENROUTER_API_KEY` | Reserved (Hy3 / other OpenRouter routes). Not used by Claude Code yet — OpenRouter's Claude Code skin is only guaranteed for Anthropic 1P models |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later (Assayer/Smith quality) |

## Hy3 note

MODEL plan originally preferred Miner → `tencent/hy3:free` on OpenRouter
(until 2026-07-21). That route is **not wired** through `claude-code-action`
because OpenRouter documents Claude Code as Anthropic-1P-only for reliability.
Miner uses DeepSeek V4 Pro until we add a non-Claude-Code runner or confirm Hy3
works end-to-end.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing auth/routing.
It should print `hitchhiker smoke test ok` via DeepSeek.

## Cost targets (MVP)

- Bootstrap (~50–100 notes) with DeepSeek Flash/Pro: treat as the active path
- Hy3 free Miner (if later wired): roughly **$100–200** cash for bootstrap
- Without Hy3 free: roughly **$200–500**
- Steady hybrid month after MVP: roughly **$50–150**

Treat these as estimates.
