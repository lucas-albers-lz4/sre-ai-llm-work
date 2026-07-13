# SRE AI LLM Work — Agent Guide

Living handbook for **SRE / LLM-ops** (not coding-agent DX). Automation is a
retargeted fork of hitchhikers-guide; **do not push to upstream**.

## Remotes

| Remote | Repo | Use |
|--------|------|-----|
| `origin` | `lucas-albers-lz4/sre-ai-llm-work` | All push/pull |
| `upstream` | steveash hitchhiker | Fetch-only reference |

Default branch: `main`. Prefer `git push origin HEAD` / `git pull`.

## What this repo is

- **`guide/`** — citation-backed chapters humans read
- **`source-notes/`** — Miner extractions (evidence corpus)
- **`agents/`** — role definitions for GitHub Actions workers
- **`registry/`** — feeds, site-crawl seeds, derived `sources.json`
- **`docs/`** — MVP setup, model routing, project board, Hy3 eval

Pipeline (separation of concerns): discover → Prospector → Miner → Assayer →
Smith → Gardener. No agent both writes and approves the same artifact.

## Model routing (MVP)

See [`docs/MODEL-ROUTING.md`](docs/MODEL-ROUTING.md).

| Worker | Model |
|--------|-------|
| Pre-screen / Prospector / site-crawl | DeepSeek Flash |
| Miner | OpenRouter `tencent/hy3:free` (trial → **2026-07-21**) |
| Assayer / Smith / Herald | DeepSeek Pro |

Secrets: `DEEPSEEK_API_KEY`, `OPENROUTER_API_KEY` (Miner), `PROJECT_PAT`
(classic `repo`+`project` — needed so `gh pr create` / issue filing triggers
downstream workflows). Claude OAuth is **not** required.

## Hard rules for local agents

1. **Do not edit `guide/`** unless implementing Smith-style synthesis or a
   human explicitly asks for a guide edit. Prefer filing/fixing source notes.
2. **Do not hand-edit `registry/sources.json`** — it is rebuilt from source-note
   front-matter (`scripts/build_registry.py` / `registry-rebuild.yml`).
3. **Do not merge `miner-eval` / `*-hy3-eval.md` PRs** into the corpus. Eval
   notes are comparison artifacts only.
4. When changing agent auth/routing, use
   `.github/actions/configure-deepseek` or `configure-openrouter-hy3`, and
   pass **`github_token: ${{ secrets.PROJECT_PAT }}`** to `claude-code-action`
   for any job that pushes branches or opens PRs.
5. Project board updates use `.github/scripts/update-project-field.sh` with
   IDs for project **#3** (`docs/PROJECT-SETUP.md`). Failures are warnings only.
6. Match existing templates: `source-notes/.template-*.md`, chapter stubs in
   `guide/`, label vocabulary in workflows/`agents/`.

## Useful commands

```bash
# Smoke DeepSeek routing
gh workflow run claude-smoke-test.yml

# Hy3 smoke / golden-set Miner replay
gh workflow run hy3-smoke-test.yml
gh workflow run miner-hy3-eval.yml -f issue_number=1

# Drain mining queue / daily discovery
gh workflow run miner-batch.yml
gh workflow run daily-scan.yml

# Project board (idempotent)
gh workflow run bootstrap-project-board.yml
```

Board: https://github.com/users/lucas-albers-lz4/projects/3

## Where to read next

| Topic | Doc |
|-------|-----|
| MVP checklist | `docs/MVP-SETUP.md` |
| Models / secrets | `docs/MODEL-ROUTING.md` |
| Agent roles | `agents/README.md` |
| Hy3 Miner trial | `docs/HY3-MINER-EVAL.md` |
| Project board | `docs/PROJECT-SETUP.md` |
| Submissions | `SUBMISSION.md` |
