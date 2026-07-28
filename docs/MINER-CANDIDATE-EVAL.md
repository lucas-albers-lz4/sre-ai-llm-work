# Miner candidate eval (cost reduction)

Miner-only program to find a cheaper (or free) model that matches current
**DeepSeek V4 Flash** Miner quality. Assayer / Smith / Herald /
contradiction stay on **DeepSeek V4 Pro**. Do not merge eval PRs.

Nemotron Ultra free failing on OpenRouter does **not** write off that
gateway — Hy3 free previously scored 4/4 Assayer APPROVE
([HY3-MINER-EVAL.md](HY3-MINER-EVAL.md)). Treat Nemotron as one bad model.

## Pass bar

Per candidate, run **sequentially** (fail fast):

```text
smoke (1-turn) → golden #1 → #2–#4 → live mining-queued trial (1 issue)
```

| Gate | Criterion |
|------|-----------|
| Smoke | `miner-candidate-smoke.yml` prints `miner candidate smoke test ok` |
| Golden | ≥3/4 Assayer APPROVE on issues #1–#4; 0 quote-fabrication fails |
| Live | One real `miner-batch` PR Assayer APPROVEs |
| Fail fast | Empty/malformed HTTP 200 mid tool-use, unparseable bodies, hard rate-limits |

Do **not** re-enable peak cron until smoke + golden + live all pass.

## Related-note retrieval (#506)

Miner jobs (production batch + candidate evals) inject lexical
cross-reference candidates from `registry/claims-index.json` into
repo-root `miner-related-notes.md` (gitignored; also copied to
`RUNNER_TEMP`) before the agent runs. Kill switch:
`disable_candidates=true` on `workflow_dispatch`, or
`MINER_DISABLE_CANDIDATES=1`. PRs get `has-candidates` / `no-candidates`.

**Acceptance (2026-07-26):** golden #1 with retrieval ON cleared ≥3/5
Cross-refs — **4/5 final pass** (mimo [#509](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/509),
ling [#510](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/510),
laguna [#511](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/511),
nemotron [#512](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/512)
APPROVE; north-mini [#513](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/513)
REQUEST CHANGES). Quote accuracy unchanged. Flash live spot-check deferred
(empty `mining-queued`). Details on [#506](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/506).
Production Miner stays on Flash; peak cron remains off.

## Workflows

```bash
# Smoke
gh workflow run miner-candidate-smoke.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free
gh workflow run miner-candidate-smoke.yml \
  -f backend=zen -f model=qwen3.5-plus
gh workflow run miner-zen-free-smoke.yml -f model=mimo-v2.5-free

# Golden-set eval (repeat issue_number=1..4)
gh workflow run miner-candidate-eval.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free -f issue_number=1
gh workflow run miner-zen-free-eval.yml \
  -f model=mimo-v2.5-free -f issue_number=1

# Live queue trial (OpenCode Zen free — chat-completions only)
gh workflow run miner-zen-free-batch.yml -f model=deepseek-v4-flash-free
# optional: -f issue_number=N

# Live queue trial (Claude Code Messages / paid Zen or OpenRouter)
gh workflow run miner-batch.yml \
  -f backend=openrouter -f model=poolside/laguna-m.1:free
gh workflow run miner-batch.yml \
  -f backend=zen -f model=qwen3.5-plus
```

Secrets: `OPENROUTER_API_KEY` (Wave A), `OPENCODE_ZEN_API_KEY` (Wave B Messages
+ Wave C OpenCode Action free). Eval PRs: labels `miner-eval` + `source-note`;
branch `miner/eval-<slug>-issue-<N>-r<run_id>`; filename `*-<slug>-eval.md`.

Legacy one-offs (`nemotron-smoke-test.yml`, `opencode-zen-smoke-test.yml`,
`miner-hy3-eval.yml`) remain for history; prefer the parameterized workflows
above.

## Candidate ladder

Test **one model fully** before the next. Confirm free OpenRouter slugs in
the live catalog before each run (IDs churn).

### Wave A — OpenRouter free (coding-oriented)

Confirm slugs against the live OpenRouter catalog before each run (IDs churn).
As of 2026-07-25, `qwen/qwen3-coder:free` is **not** listed.

| # | Model | Smoke | #1 | #2 | #3 | #4 | Live | Notes / decision |
|---|-------|-------|----|----|----|----|------|------------------|
| 1 | `poolside/laguna-m.1:free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30164857692)) | **fail** — no eval PR after ~27m; aborted as not Miner-capable ([cancelled](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30164900980)) | — | — | — | — | Smoke ≠ multi-turn. Skip sibling Laguna free variants. |
| 2 | `poolside/laguna-xs-2.1:free` / `laguna-s-2.1:free` | skipped | — | — | — | — | — | Same family as M.1; not worth another 27m hang |
| 3 | `cohere/north-mini-code:free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30165922607)) | [PR #496](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/496) **REQUEST CHANGES** (cross-refs) | — | — | — | — | Ran clean (~2m, no hang; depth/accuracy/completeness pass) but same "first source note in repo" cross-ref fabrication as Wave C free models. Fail-fast after #1. |

**Wave A decision (2026-07-25):** No free OpenRouter coding model cleared the Assayer bar. Laguna M.1 hung ~27m with no eval PR (smoke had passed); north-mini-code completed golden #1 fast but failed cross-references.

Skip: `nvidia/nemotron-3-ultra-550b-a55b:free` (already failed multi-turn).

### Wave B — OpenCode Zen Messages (cheap paid)

Only `/v1/messages` models. Requires `OPENCODE_ZEN_API_KEY`.

| # | Model | Smoke | #1 | #2 | #3 | #4 | Live | Notes / decision |
|---|-------|-------|----|----|----|----|------|------------------|
| 1 | `qwen3.5-plus` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30165953323)) | [PR #488](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/488) **APPROVE** (accidentally auto-merged then removed from corpus) | [PR #489](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/489) **APPROVE** | [PR #490](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/490) REQUEST CHANGES | [PR #491](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/491) **APPROVE** | deferred — queue empty ([batch](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30167011081) no-op) | **3/4 APPROVE** clears golden bar. Live when next `mining-queued` issue: `gh workflow run miner-batch.yml -f backend=zen -f model=qwen3.5-plus`. No peak cron until that live Assayer APPROVE. |
| 2 | `qwen3.7-plus` | | | | | | | not needed yet — 3.5-plus leading |
| 3 | `claude-haiku-4.5` (fallback) | | | | | | | |

**Wave B interim decision (2026-07-25):** `qwen3.5-plus` cleared golden (3/4)
but live trial never ran (empty queue). **Final:** park it; stay on Flash
(see Final decision below). Assayer auto-merge now skips `miner-eval`.

### Wave C — Zen free chat-completions (OpenCode Action runner)

These Zen free IDs are `/v1/chat/completions` only — they **cannot** use
Claude Code + `configure-opencode-zen` (Messages). Eval uses
`anomalyco/opencode/github` with `model: opencode/<id>` and
`OPENCODE_ZEN_API_KEY`. Job timeout **12m**. If OpenCode fails/cancels
after pushing the eval branch, salvage still opens the `miner-eval` PR and
dispatches Assayer. Related-note candidates are written to repo-root
`miner-related-notes.md` (gitignored).

**OpenCode hang (#500, closed):** root cause was headless `opencode github run`
blocking forever on an interactive `external_directory` ask when the prompt
wrote `/tmp/miner-eval-pr-body.md` — not a FreeUsageLimitError retry and not
a stalled stream ([BISECT.md Step 0b](https://github.com/lucas-albers-lz4/opencode-hang-repro/blob/main/docs/BISECT.md)).
Fixed in [#561](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/561):
PR bodies go to in-workspace `.miner-eval-pr-body.md` / `.miner-pr-body.md`
(gitignored) in zen-free, candidate-eval, and miner-batch. Verify run
([30208634452](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30208634452))
exited in ~3m with zero `asking {` events. Salvage remains useful for
intermittent stream failures and other non-clean exits.

| Model | Agent signals (indicative) | Verdict |
|-------|----------------------------|---------|
| `nemotron-3-ultra-free` | Terminal-Bench 56.4; Toolathlon 34.3; prior OpenRouter Miner fail | Tried — fail (REQUEST CHANGES + stream error) |
| `mimo-v2.5-free` | MiMo V2.5 family agent/coding-first | Try first |
| `ling-3.0-flash-free` | InclusionAI agent MoE; vendor SWE ~72 multilingual | Try second |
| `laguna-s-2.1-free` | Terminal-Bench 70.2; Toolathlon 49.7; stronger than M.1 | Tried — fail (REQUEST CHANGES) |
| `deepseek-v4-flash-free` | Same family as production Miner Flash; Zen free chat-completions | **4/4 golden APPROVE** (OpenCode hang class remains; salvage works) |

```bash
gh workflow run miner-zen-free-smoke.yml -f model=mimo-v2.5-free
gh workflow run miner-zen-free-eval.yml -f model=mimo-v2.5-free -f issue_number=1
```

| # | Model | Smoke | #1 | #2 | #3 | #4 | Live | Notes / decision |
|---|-------|-------|----|----|----|----|------|------------------|
| 1 | `mimo-v2.5-free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30167553119)) | [PR #492](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/492) **REQUEST CHANGES** (cross-refs) | — | — | — | — | Fail-fast after #1; proceed to Ling |
| 2 | `ling-3.0-flash-free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30168573200)) | [PR #493](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/493) **REQUEST CHANGES** | — | — | — | — | Fail-fast after #1; proceed to Laguna S |
| 3 | `laguna-s-2.1-free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30168739432)) | [PR #494](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/494) **REQUEST CHANGES** | — | — | — | — | Completed in ~5m (no hang); Assayer still REQUEST CHANGES |
| 4 | `nemotron-3-ultra-free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30171998659)) | [PR #495](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/495) first Assayer **REQUEST CHANGES** (cross-refs); re-review **APPROVE** (same note, no Miner fix) | — | — | — | — | Eval job stream-failed after push; PR salvaged. Fail-fast: do not continue #2–#4 (Assayer variance + stream fragility; peers failed cross-refs cleanly) |
| 5 | `deepseek-v4-flash-free` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30178170790)) | [PR #498](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/498) **APPROVE** | [PR #499](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/499) **APPROVE** (eval run timed out after push; PR salvaged) | [PR #502](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/502) **APPROVE** (12m cancel + salvage) | [PR #504](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/504) **APPROVE** (12m cancel + salvage) | [PR #569](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/569) **APPROVE** (auto-merged) — live [#567](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/567) ([drain](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30210465311)); **2nd live** [#608](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/608) / [PR #612](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/612) **APPROVE** (merged) via [30328991114](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30328991114) (#606 validation; citation rework on twin [#613](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/613) then closed as dup) | **4/4 golden + 2× live Assayer APPROVE**. Hang mitigated [#561](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/561). Peak premise died (#571). **Manual/dispatch + eval only** (Phase 1: peak cron is Big Pickle). |
| 6 | `big-pickle` | pass ([run](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30212161336)) | [PR #577](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/577) content pass (Assayer REQUEST CHANGES mainly from close/"do not merge" directive) | [PR #578](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/578) **APPROVE** | [PR #579](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/579) **APPROVE** | [PR #580](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/580) **APPROVE** | [PR #611](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/611) **APPROVE** (auto-merged) — live [#610](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/610) via [30328696268](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30328696268) (#606) | Fingerprint: OpenCode `llm.model=big-pickle`. **Live Assayer APPROVE (#606)**. **Phase 1 scheduled** peak UTC `1-3,6-9`. Privacy: Zen may retain free Big Pickle prompts. |

**Wave C decision (2026-07-26 / updated 2026-07-27):** First four Zen free
candidates failed golden #1 (cross-refs). `deepseek-v4-flash-free` cleared
**4/4** Assayer APPROVE on golden and **one live** drain (#564 / #566).
Hang fixed [#561](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/561).
**#571:** peak premise died (N=3 peak + N=3 off-peak extractions); peak cron
enabled on `miner-zen-free-batch.yml`. Fail-closed + no-op retry: #572.
`big-pickle` clears #2–#4 APPROVE as alternate free.

## Final decision (2026-07-27 / updated 2026-07-28 Phase 1)

**Off-peak:** DeepSeek V4 Flash (paid, direct API) via `miner-batch.yml`.
**Peak (Phase 1):** Zen free `big-pickle` via `miner-zen-free-batch.yml`
cron `:19` at UTC `1-3,6-9`. `deepseek-v4-flash-free` is manual/dispatch +
eval only.

- Peak premise (free DeepSeek deprioritized at DeepSeek peak) **died** —
  N=3/3 peak golden #1 workflows succeeded ([30229984461](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30229984461),
  [30230090171](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30230090171),
  [30230156359](https://github.com/lucas-albers-lz4/sre-ai-llm-work/actions/runs/30230156359));
  off-peak N=3/3 likewise.
- `$/note` zen-free peak = **$0** (Zen free tier). Qwen3.5-plus parked (Zen
  list price worse than Flash on output). GPT-5 Nano out of scope.
- `big-pickle`: **Phase 1 scheduled** on all peak hours (live APPROVE #611 /
  #606); gateway id distinct from Flash-free (stealth backing may change).
- Assayer/Smith/Herald stay on DeepSeek V4 Pro (unchanged).

**#606 validation (2026-07-28):** Non-empty `mining-queued` drains succeeded for
both finds — Big Pickle live APPROVE; Flash-free second live APPROVE (merged
#612). Fail-closed path: no junk `opencode/dispatch-*` / no-op retry needed.
Peak cron briefly **split**, then **Phase 1** collapsed to `big-pickle` only
(Flash-free off the schedule for ops simplicity / suspected free-tier quality).

Scorecard detail above; routing: [`MODEL-ROUTING.md`](MODEL-ROUTING.md).
Related: [#328](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/328),
[#571](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/571),
[#606](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/606).

### Gaps vs original plan (accepted / deferred)

| Item | Status |
|------|--------|
| Wave A `qwen/qwen3-coder:free` | Not in live OpenRouter catalog (2026-07-25) |
| Wave A `north-mini-code` golden | **Closed 2026-07-25** — PR #496 REQUEST CHANGES (cross-refs); Wave A exhausted |
| Wave B `qwen3.7-plus` / `claude-haiku-4.5` | Not run — 3.5-plus already cleared golden; staying on Flash |
| Live `mining-queued` trial (any candidate) | **Done 2026-07-26** — `deepseek-v4-flash-free` live [#567](https://github.com/lucas-albers-lz4/sre-ai-llm-work/issues/567) / PR [#569](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/569) Assayer APPROVE (#564) |
| $/note Flash vs Zen/OpenRouter comparison | **Recorded 2026-07-27** — zen-free peak `$0`/note; paid Flash remains off-peak cost floor; Qwen Plus not competitive on list price |
| Peak cron re-enable | **Done 2026-07-27** — `miner-zen-free-batch.yml` schedule (#571) |
| Assayer skip-merge for `miner-eval` | Done (PR #488 leak fixed) |
| OpenCode post-push hang (#500) | **Closed 2026-07-26** — headless `external_directory` ask on `/tmp`; fixed [#561](https://github.com/lucas-albers-lz4/sre-ai-llm-work/pull/561) |

## Decision rules

| Outcome | Action |
|---------|--------|
| OpenRouter free clears bar + stable live | Prefer for peak-fill (optionally more Miner hours) |
| Zen Qwen Plus ≤ Flash cost at equal quality | Route peak (and/or more Miner) via Zen; Flash fallback |
| Free fails multi-turn; paid Zen wins | Zen for peak only; off-peak Flash |
| Nothing beats Flash | Stay on Flash; revisit when catalog changes |

## Golden set

| Issue | Baseline note |
|-------|---------------|
| #1 | `source-notes/blog-pagerduty-sre-agent-architecture.md` |
| #2 | `source-notes/blog-honeycomb-instrumenting-ai-agents-opentelemetry.md` |
| #3 | `source-notes/blog-incidentio-ai-sre-incident-run.md` |
| #4 | `source-notes/blog-pagerduty-production-ai-agent-gaps.md` |
