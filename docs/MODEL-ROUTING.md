# Model routing (MVP)

Agent workflows use `anthropics/claude-code-action` (and the Claude Code CLI)
routed to **DeepSeek's Anthropic-compatible API** via
`.github/actions/configure-deepseek`. OpenRouter / Zen Messages wiring remains
in `miner-batch.yml` for **manual trials** only. Production Miner drains use
**`miner-zen-free-batch.yml`** (OpenCode Action → Zen free `big-pickle`).

**2026-08-01 Phase 3 cutover (Flash 0731):** Scheduled Miner is **100%** Zen
free `big-pickle` (`19,49 * * * *`). Paid Flash Miner is dispatch-only.
Assayer / Smith / Herald / Contradiction moved from `deepseek-v4-pro[1m]` to
**`deepseek-v4-flash[1m]`** (Flash 0731 agent benches beat Pro Preview; same
API id `deepseek-v4-flash`). Pro retired from production routing until a later
re-eval. `deepseek-v4-flash-free` remains manual/dispatch + eval only.

**2026-08-02 Assayer spot-check ruling (#735):** Flash burned the 25-turn
review budget re-downloading PDFs (`pip install pypdf`, full-text extract,
regex every claim) and never wrote a review. `agents/ASSAYER.md` + Assayer
workflow prompt now require HEAD-only URL checks, at most 2–3 quote
spot-checks, no primary-source body download / package installs, and writing
the review promptly. **`--max-turns` stays 25** — do not raise the budget to
paper over re-mining.

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
| **Miner (production)** | Zen free `big-pickle` | `miner-zen-free-batch.yml` cron `:19,:49` every hour (48 slots/day; 1 issue/run). Other Zen free models remain manual dispatch / eval. |
| **Miner (manual)** | `deepseek-v4-flash` etc. | `miner-batch.yml` workflow_dispatch only; peak_guard skips Flash in UTC `1–3`/`6–9` |
| Assayer / Smith / Herald / Contradiction | `deepseek-v4-flash[1m]` | Review & synthesis (1M context); was Pro until Flash 0731 |

Site-crawl (`scripts/scan-sites.py`) calls the same Anthropic-compatible
Messages API with `DEEPSEEK_API_KEY` + `SITE_CRAWL_MODEL=deepseek-v4-flash`.

## Secrets

| Secret | Purpose |
|--------|---------|
| `DEEPSEEK_API_KEY` | **Required** — all agent workflows + site-crawl screener |
| `PROJECT_PAT` | GitHub Projects + issue/PR events that must trigger workflows |
| `OPENROUTER_API_KEY` | Optional — manual Miner OpenRouter trials / Hy3 / Nemotron smoke |
| `OPENCODE_ZEN_API_KEY` | **Required for scheduled Zen Miner** — `miner-zen-free-batch.yml` + manual Zen free / `backend=zen` |
| `ANTHROPIC_API_KEY` / `CLAUDE_CODE_OAUTH_TOKEN` | Optional Claude ceiling later |

## Miner schedule (Phase 3 — all Big Pickle)

DeepSeek may bill **2×** during peak windows (UTC **01:00–04:00** and
**06:00–10:00**). Scheduled Miner is entirely Zen free **`big-pickle`**
(`$/note` ≈ $0 on free tier), so peak surcharge does not apply to Miner.
Manual Flash via `miner-batch.yml` still **fail-closes** if a tick starts in
hours `1–3` or `6–9`.

| Workflow | Cron (UTC) | Backend |
|----------|------------|---------|
| `miner-zen-free-batch.yml` | `:19` and `:49` every hour | Zen free `big-pickle` |
| `miner-batch.yml` | *(none — dispatch only)* | Manual Flash / trials |
| `daily-scan.yml` | `12:02` daily | DeepSeek Flash |
| `smith-on-source-merge.yml` | Sat `15:19`, Thu `00:02` | DeepSeek Flash `[1m]` |
| `assayer-drain.yml` | `:05` hours `0,4,5,10–23` UTC | Assayer Flash `[1m]` (drain-only) |
| `gardener.yml` | Sun `14:02` (Python) | — |
| `herald-weekly.yml` | Sun `16:02` | DeepSeek Flash `[1m]` |

Minutes are offset from `:00` to reduce top-of-hour Actions contention.
Manual runs: `gh workflow run miner-zen-free-batch.yml -f model=big-pickle`;
`gh workflow run miner-batch.yml -f backend=flash` (trial);
`gh workflow run miner-zen-free-batch.yml -f model=deepseek-v4-flash-free` (eval).

Event-driven jobs (pre-screen, Prospector) cannot defer to off-peak without
queueing; keep those prompts short. **Assayer** is drain-only (#1042): events
enqueue; Flash runs from `assayer-drain.yml` off-peak cron only.

## Peak-fill history → Phase 3

**2026-07-23:** OpenRouter Nemotron free failed real Miner batches (Claude Code
gateway errors). Peak cron removed from `miner-batch.yml`.

**2026-07-26:** Zen free `deepseek-v4-flash-free` cleared golden + live Assayer
(#564 / PR #569) via `miner-zen-free-batch.yml`.

**2026-07-27 (#571):** Peak premise (free DeepSeek deprioritized in DeepSeek
peak windows) **died** — N=3 peak + N=3 off-peak golden #1 all extracted.
Peak cron enabled on `miner-zen-free-batch.yml`. Fail-closed junk-PR + one
no-op retry shipped in #572.

**2026-07-28:** Peak schedule briefly **split** after #606, then **Phase 1** —
all peak hours (`19 1-3,6-9 * * *`) → `big-pickle`.

**2026-07-29 / merged 2026-07-31 Phase 2 (#656):** Expand `big-pickle` to
half of Miner crons (`19 0-11 * * *`); Flash on `19 12-23 * * *`. Gate: N=2
live Assayer APPROVE (PRs #698 / #699). Peak Flash drift guard: #701.

**2026-08-01 Phase 3:** All scheduled Miner → `big-pickle` (`19,49 * * * *`);
`miner-batch.yml` schedule removed. Assayer/Smith/Herald/Contradiction →
`deepseek-v4-flash[1m]` after Flash 0731 upgrade.

```bash
gh workflow run miner-zen-free-smoke.yml -f model=big-pickle
gh workflow run miner-zen-free-eval.yml -f model=big-pickle -f issue_number=1
gh workflow run miner-zen-free-batch.yml -f model=big-pickle
gh workflow run miner-zen-free-batch.yml -f model=deepseek-v4-flash-free   # eval / A-B
```

Requires `OPENCODE_ZEN_API_KEY` for zen-free schedule. Zen `/v1/messages` for
Claude Code (qwen3.5/3.6/3.7 plus/max, claude-*) remains manual only.

## Hy3 note (historical)

Miner ran OpenRouter `tencent/hy3:free` through **2026-07-21** after a
golden-set replay scored 4/4 Assayer APPROVE (`docs/HY3-MINER-EVAL.md`).
Keep `configure-openrouter-hy3` + `miner-hy3-eval.yml` for A/B if needed.

## Smoke test

Dispatch `.github/workflows/claude-smoke-test.yml` after changing DeepSeek
auth/routing. It should print `hitchhiker smoke test ok` via DeepSeek.

Dispatch `.github/workflows/nemotron-smoke-test.yml` only when validating
OpenRouter candidates (smoke ≠ Miner reliability).

## Cost targets (MVP)

- Triage / crawl / Assayer / Smith / Herald: DeepSeek Flash (Flash `[1m]` for
  long-context review)
- Scheduled Miner: Zen free `big-pickle` (`$/note` ≈ $0)
- Steady hybrid month after MVP: roughly **$50–150** (estimate); Pro spend
  removed from production path

Treat these as estimates.

## Flash caller inventory (production)

Cost program umbrella: [#767](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/767).
Phase C (Assayer drain-only): [#1042](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1042).
Orthogonal OR fp8 lane (next): [#1113](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1113).

| Caller | Workflow / script | Model | Trigger | Peak exposure |
|--------|-------------------|-------|---------|---------------|
| Pre-screen | `source-pipeline.yml` | `deepseek-v4-flash` | `issues: opened`, `issues: labeled` | Event-driven |
| Prospector | `source-pipeline.yml` (after pre-screen job) | `deepseek-v4-flash` | same workflow, pre-screen pass | Event-driven |
| Scribe | `scribe.yml` | `deepseek-v4-flash` | `issues: labeled` (`sticky-notes`) | Event-driven |
| Site-crawl screener | `scan-sites.py` via `daily-scan.yml` | `deepseek-v4-flash` | cron `12:02` UTC | Off-peak |
| Assayer review | `assayer.yml` via `assayer-drain.yml` | `deepseek-v4-flash[1m]` | off-peak drain cron (`force=true`) | **Off-peak only** |
| Assayer enqueue | `assayer.yml` prepare | — (no Flash) | PR / Miner / Smith dispatch | Queue only |
| Assayer Smith/Miner rework | `assayer.yml` | `deepseek-v4-flash[1m]` | post-rework `force=true` | Follows drain / force |
| Smith synthesis | `smith-on-source-merge.yml` | `deepseek-v4-flash[1m]` | Sat/Thu cron | Thu `00:02` spill watch |
| Smith rework | `smith-rework.yml` | `deepseek-v4-flash[1m]` | PR comment `/rework` or `/rebase` | Event-driven (`force=true` Assayer) |
| Herald | `herald-weekly.yml` | `deepseek-v4-flash[1m]` | Sun cron | Off-peak |
| Contradiction assess + resolve | `contradiction-resolver.yml` | `deepseek-v4-flash[1m]` | `issues: labeled` (two jobs) | Event-driven |
| Manual Flash Miner | `miner-batch.yml` | `deepseek-v4-flash` | dispatch only | peak_guard skip |
| Smoke | `claude-smoke-test.yml` | `deepseek-v4-flash` | manual | Negligible |

### Assayer drain-only (#1042)

Event-driven Assayer (PR open/sync/label, Miner/Smith `workflow_dispatch` with
`pr_number` only) **does not call Flash**. It applies `assayer-queued` and a
sticky `<!-- assayer-queue: sha=… -->` comment. Reviews run from
`assayer-drain.yml`:

| | |
|--|--|
| Cron (UTC) | `5 0,4,5,10-23 * * *` — never hours 1–3 or 6–9 (DeepSeek peak) |
| Cap | 5 PRs/tick (bump to 8 if queue age grows; never cut Miner) |
| Dispatch | `assayer.yml` with `force=true` via `PROJECT_PAT` |
| Urgent | Manual `gh workflow run assayer.yml -f pr_number=N -f force=true` |
| Dedupe | Review comments carry `<!-- assayer-verdict: sha=… -->` |

Peak control is **schedule only** — no runtime peak helper. Orthogonal cost
cut ([#1113](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/1113)):
static OpenRouter fp8 lane for some Flash callers; do not double-count Assayer
dollars until Assayer is explicitly moved to OR.

**Site-crawl input:** `scan-sites.py` sends **full URL strings** (scheme + host +
path) to Flash for relevance screening from path/name only (“you cannot read the
pages”). It does **not** fetch or send page HTML. Main-content extract /
content-hash skip ([#658](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/658))
only saves tokens if the screener is redesigned to send page text.

**Claude Code Action jobs** (Assayer, Smith, Prospector, etc.) may not expose
cache hit/miss in Actions logs. For Phase A attribution, **`scan-sites.py` is
the instrumented direct Messages API path** (see below).

### Site-crawl usage logging

After each Flash screening call, `scan-sites.py` prints structured lines:

```text
SITE_CRAWL_USAGE status=ok model=deepseek-v4-flash seed=<id> urls=<n> input_tokens=... output_tokens=... cache_read=... cache_miss=... cache_creation=... unparsed_urls=...
SITE_CRAWL_USAGE_TOTAL calls=... errors=... input_tokens=... ...
```

Field mapping (Messages `usage` block):

| Log field | Primary API fields | Notes |
|-----------|-------------------|-------|
| `input_tokens` | `input_tokens`, `prompt_tokens` | |
| `output_tokens` | `output_tokens`, `completion_tokens` | |
| `cache_read` | `prompt_cache_hit_tokens`, `cache_read_input_tokens` | DeepSeek hit / Anthropic read |
| `cache_miss` | `prompt_cache_miss_tokens` | DeepSeek uncached prompt input only |
| `cache_creation` | `cache_creation_input_tokens` | Anthropic cache write; usually 0 on DeepSeek |

`unparsed_urls` counts input URLs with **no matching model output line** after
substring URL match. Those URLs still become `pending` and may be **filed** on
the same run — not deferred to a later rescreen.

Grep after `daily-scan.yml`:

```bash
gh run list --workflow daily-scan.yml --limit 1
gh run view <run_id> --log | rg 'SITE_CRAWL_USAGE'
```

### Prompt cache hygiene

Production workflows that use Claude Code load **byte-stable** role files into
the system-prompt prefix (no run IDs or timestamps in the cached block):

| Workflow | Mechanism | Role file |
|----------|-----------|-----------|
| `assayer.yml` (review) | `APPEND_SYSTEM_PROMPT` | `agents/ASSAYER.md` |
| `source-pipeline.yml` (Prospector) | `APPEND_SYSTEM_PROMPT` | `agents/PROSPECTOR.md` |
| `herald-weekly.yml` | `APPEND_SYSTEM_PROMPT` | `agents/HERALD.md` |
| `miner-batch.yml` | `APPEND_SYSTEM_PROMPT` | `agents/MINER.md` |
| `contradiction-resolver.yml` | `APPEND_SYSTEM_PROMPT` | `agents/ASSAYER.md` |
| `smith-on-source-merge.yml` | `--append-system-prompt` | `agents/SMITH.md` |
| `smith-rework.yml`, Assayer rework steps | `--append-system-prompt` | `agents/SMITH.md` / `MINER.md` |

Not covered here (different stack / no role append): production Miner
(`miner-zen-free-batch.yml`, OpenCode), pre-screen in `source-pipeline.yml`
(inline prompt), `scribe.yml` (inline prompt).

Rules:

- Cached prefix = file contents only (`cat agents/*.md`).
- Variable content (PR diff, issue body, labels) stays in the **user** prompt.
- Do **not** prepend timestamps, run IDs, or SHA to `APPEND_SYSTEM_PROMPT`.

Audit (2026-08-28): all production `APPEND_SYSTEM_PROMPT` heredocs use plain
`cat agents/<ROLE>.md` with no dynamic prefix. No workflow changes required.
