# MVP setup — SRE AI LLM Work

## 1. Repo

This repository is the retargeted fork:

- GitHub: `https://github.com/lucas-albers-lz4/sre-ai-llm-work`
- Upstream pipeline inspiration: steveash/hitchhikers-guide-to-ai-native-engineering

## 2. Required secrets (Settings → Secrets → Actions)

1. `PROJECT_PAT` — classic PAT with `repo` + `project` (issue filing + board)
2. `OPENROUTER_API_KEY` — load **$10** credits once (unlocks 1k free-model RPD)
3. `DEEPSEEK_API_KEY` — top up ~$20–50 for bootstrap
4. Optional: `CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_API_KEY` for Assayer/Smith ceiling
5. Optional: GLM / LongCat keys when you wire those workers

## 3. First human tasks after push

1. Replace placeholders in `registry/trusted-feeds.json` with feeds that actually
   resolve (verify each URL in a browser/feed reader).
2. Add 2–5 site-crawl seeds with SRE-relevant `scope` hints.
3. File 3–5 seed `[source]` issues manually to smoke-test Prospector → Miner.
4. Skim Assayer on the first source-note PRs; comment `/rework` if needed.
5. After ~20–30 notes, dispatch Smith (`smith-on-source-merge.yml`) and review
   the first `guide-update` PR yourself.

## 4. What was wiped

- All prior `source-notes/*.md` (coding-agent corpus)
- Guide chapters replaced with SRE stubs
- `CONTRADICTIONS.md` reset
- Registry discovery state reset
- Sticky notes reset per new chapters

Templates under `source-notes/.template-*` were kept.

## 5. Cap knobs

- `DAILY_SCAN_CAP` in `.github/workflows/daily-scan.yml` (default 20)
- Miner `BATCH_SIZE` in `miner-batch.yml` (default 2)

Lower these during MVP if you want slower burn.
