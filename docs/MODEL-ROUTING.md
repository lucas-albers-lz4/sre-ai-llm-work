# Model routing (MVP)

Default workflows invoke `anthropics/claude-code-action` with Haiku / Sonnet /
Opus. For the SRE fork MVP, prefer cheaper models per worker while keeping
the same agent prompts.

## Recommended worker → model map

| Worker | Primary | Fallback |
|--------|---------|----------|
| Pre-screen / Prospector / Scribe / Site-crawl | DeepSeek V4 Flash | GPT-5.4 nano |
| Miner | Hy3 (`tencent/hy3:free` on OpenRouter until 2026-07-21) | DeepSeek V4 Pro |
| Assayer | GLM-5.2 | DeepSeek V4 Pro / LongCat-2.0 |
| Smith | GLM-5.2 | Claude Sonnet 4.6 (quality ceiling) |
| Repo Scout | GLM-5.2 | LongCat-2.0 / DeepSeek V4 Pro |

## Secrets

| Secret | Purpose |
|--------|---------|
| `OPENROUTER_API_KEY` | Hy3 free + other OpenRouter routes ($10 credits unlocks 1k free RPD) |
| `DEEPSEEK_API_KEY` | Direct DeepSeek (preferred for volume; Anthropic-compatible base URL) |
| `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling / legacy path |
| `PROJECT_PAT` | GitHub Projects + issue filing that triggers workflows |

## DeepSeek via Anthropic-compatible endpoint

DeepSeek serves `https://api.deepseek.com/anthropic`. For local/CLI experiments:

```bash
export ANTHROPIC_BASE_URL=https://api.deepseek.com/anthropic
export ANTHROPIC_API_KEY=$DEEPSEEK_API_KEY
# then use model ids deepseek-v4-flash / deepseek-v4-pro per DeepSeek docs
```

Wiring the same into every GitHub Action is a follow-up: either set
`ANTHROPIC_BASE_URL` + key in workflow env, or replace
`claude-code-action` with an OpenRouter/DeepSeek runner. MVP ships the domain
retarget first; keep Claude OAuth working until the runner swap is tested.

## Cost targets (MVP)

- Bootstrap (~50–100 notes) with Hy3 free Miner: roughly **$100–200** cash
- Without Hy3 free: roughly **$200–500**
- Steady hybrid month after MVP: roughly **$50–150**

See analysis notes in the originating conversation; treat these as estimates.
