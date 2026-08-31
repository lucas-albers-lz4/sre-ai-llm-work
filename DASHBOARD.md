# Guide Dashboard

_Generated 2026-08-31 (UTC) by `scripts/generate_dashboard.py`._

Content-derived metrics for the living guide. Refreshed daily by
`.github/workflows/daily-scan.yml`. For workflow status (PRs, issues,
scanner queues) see the GitHub Project linked from README.md.

| Chapter | Sources | Oldest source | Stale % | Lines (Δ7d) |
|---|---|---|---|---|
| `guide/00-principles.md` | 9/30 | 2025-12-15 (`blog-promptfoo-ai-regulation-2025`) | 0% | 227 (n/a) |
| `guide/01-incident-response.md` | 3/30 | — | 0% | 231 (n/a) |
| `guide/02-observability.md` | 6/30 | 2021-10-12 (`docs-google-sre-reliable-data-processing-minimal-toil`) | 0% | 324 (n/a) |
| `guide/03-runbooks-and-agents.md` | 7/30 | 2025-11-10 (`blog-promptfoo-ai-orchestrated-cyberattacks`) | 0% | 322 (n/a) |
| `guide/04-oncall-and-toil.md` | 7/30 | — | 0% | 324 (n/a) |
| `guide/05-llm-ops-reliability.md` | 11/30 | 2025-12-12 (`blog-promptfoo-asr-not-portable-metric`) | 0% | 614 (n/a) |
| `guide/06-security-and-trust.md` | 13/30 | 2025-05-22 (`blog-promptfoo-red-team-claude`) | 0% | 522 (n/a) |

**Source cap**: 30 per chapter (see `hitchhiker.config.json`). 
Chapters at the cap are marked ⚠ and block new Smith additions until 
the Gardener prunes.

**Staleness**: percentage of cited source notes whose `last_checked` 
frontmatter field is more than 90 days old. Matches the 
`[stale]` confidence tag defined in README.md.

**Δ7d**: line-count delta vs. the most recent commit from at least 7 
days ago. `n/a` means the repo (or this chapter) is younger than a week.
