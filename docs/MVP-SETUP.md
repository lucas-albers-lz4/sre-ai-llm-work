# MVP setup — SRE AI LLM Work

## 1. Repo

This repository is the retargeted fork:

- GitHub: `https://github.com/lucas-albers-lz4/sre-ai-llm-work`
- Upstream pipeline inspiration: steveash/hitchhikers-guide-to-ai-native-engineering

## 2. Required secrets (Settings → Secrets → Actions)

1. `PROJECT_PAT` — classic PAT with `repo` + `project` (issue filing + board)
2. `DEEPSEEK_API_KEY` — **required** for all agent workflows (Anthropic-compatible)
3. `OPENROUTER_API_KEY` — optional while Miner peak-fill cron is off (manual OpenRouter trials / Hy3 / Nemotron smoke)
4. Optional: `CLAUDE_CODE_OAUTH_TOKEN` / `ANTHROPIC_API_KEY` for a Claude quality ceiling later
5. Optional: GLM / LongCat keys when you wire those workers

See [`docs/MODEL-ROUTING.md`](MODEL-ROUTING.md) for the wired Flash/Pro map.

## 3. First human tasks after push

1. ~~Replace placeholders in `registry/trusted-feeds.json`~~ — done (15 verified feeds).
2. ~~Add 2–5 site-crawl seeds with SRE-relevant `scope` hints.~~ — done (5 seeds in `registry/site-crawl-seeds.json`).
3. ~~Dispatch `claude-smoke-test.yml` to confirm DeepSeek routing.~~ — passed.
4. ~~File 3–5 seed `[source]` issues manually to smoke-test Prospector → Miner.~~ — 4 issues → 4 merged source notes.
5. ~~Skim Assayer on the first source-note PRs; comment `/rework` if needed.~~ — quality OK.
6. **Next:** let Daily Scanner + trusted feeds grow the corpus (~20–30 notes), then dispatch Smith (`smith-on-source-merge.yml`) and review the first `guide-update` PR yourself.

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
