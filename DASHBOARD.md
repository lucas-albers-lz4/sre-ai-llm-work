# Guide Dashboard

_Generated 2026-08-09 (UTC) by `scripts/generate_dashboard.py`._

Content-derived metrics for the living guide. Refreshed daily by
`.github/workflows/daily-scan.yml`. For workflow status (PRs, issues,
scanner queues) see the GitHub Project linked from README.md.

| Chapter | Sources | Oldest source | Stale % | Lines (Δ7d) |
|---|---|---|---|---|
| `guide/00-principles.md` | 3/30 | 2025-12-15 (`blog-promptfoo-ai-regulation-2025`) | 0% | 145 (n/a) |
| `guide/01-incident-response.md` | 0/30 | — | 0% | 14 (n/a) |
| `guide/02-observability.md` | 3/30 | 2026-06-29 (`blog-honeycomb-instrumenting-ai-agents-opentelemetry`) | 0% | 216 (n/a) |
| `guide/03-runbooks-and-agents.md` | 4/30 | 2025-11-10 (`blog-promptfoo-ai-orchestrated-cyberattacks`) | 0% | 229 (n/a) |
| `guide/04-oncall-and-toil.md` | 0/30 | — | 0% | 13 (n/a) |
| `guide/05-llm-ops-reliability.md` | 5/30 | 2025-12-12 (`blog-promptfoo-asr-not-portable-metric`) | 0% | 299 (n/a) |
| `guide/06-security-and-trust.md` | 7/30 | 2025-11-10 (`blog-promptfoo-ai-orchestrated-cyberattacks`) | 0% | 342 (n/a) |

**Source cap**: 30 per chapter (see `hitchhiker.config.json`). 
Chapters at the cap are marked ⚠ and block new Smith additions until 
the Gardener prunes.

**Staleness**: percentage of cited source notes whose `last_checked` 
frontmatter field is more than 90 days old. Matches the 
`[stale]` confidence tag defined in README.md.

**Δ7d**: line-count delta vs. the most recent commit from at least 7 
days ago. `n/a` means the repo (or this chapter) is younger than a week.
