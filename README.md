# SRE AI LLM Work

A living, opinionated, citation-backed handbook for SREs and platform engineers
using AI/LLMs in operations — and running LLM systems reliably. Updated as new
patterns emerge and old ones decay.

**Fork lineage:** automation pipeline adapted from
[hitchhikers-guide-to-ai-native-engineering](https://github.com/steveash/hitchhikers-guide-to-ai-native-engineering).
Domain retargeted from AI coding agents → **SRE AI / LLM work**.

**This guide is point-in-time.** Every recommendation cites its source. Every
claim states its confidence level.

---

## Read the Guide

The guide lives in [`guide/`](guide/):

- [Principles](guide/00-principles.md) — Mental models for AI in SRE
- [Incident Response](guide/01-incident-response.md) — AI during pages and SEVs
- [Observability](guide/02-observability.md) — Logs, metrics, traces + LLMs
- [Runbooks and Agents](guide/03-runbooks-and-agents.md) — Encoding ops knowledge
- [On-call and Toil](guide/04-oncall-and-toil.md) — Cutting toil without new risk
- [LLM Ops Reliability](guide/05-llm-ops-reliability.md) — SLOs, evals, cost, failure modes
- [Security and Trust](guide/06-security-and-trust.md) — Threat model for AI in ops
- [Sources](guide/SOURCES.md) — Master index of cited sources

### Trust Model

| Tag | Meaning |
|-----|---------|
| `[settled]` | Multiple independent sources confirm. Safe to rely on. |
| `[emerging]` | 2-3 sources, consistent but limited evidence. |
| `[anecdotal]` | Single practitioner report. Interesting but unverified. |
| `[editorial]` | Our synthesis — not directly from a source. |
| `[stale]` | Source is >90 days old and hasn't been re-verified. |

---

## Improve the Guide

- [**Source submission**](.github/ISSUE_TEMPLATE/source-submission.yml)
- [**Seed site**](.github/ISSUE_TEMPLATE/seed-site.yml)
- [**Practitioner repo**](.github/ISSUE_TEMPLATE/practitioner-repo.yml)
- [**Failure report**](.github/ISSUE_TEMPLATE/failure-report.yml)
- [**Sticky notes**](.github/ISSUE_TEMPLATE/sticky-notes.yml)

See [SUBMISSION.md](SUBMISSION.md) and [`agents/README.md`](agents/README.md).

---

## MVP / cost posture

Bootstrap targets cheap models for volume (DeepSeek Flash/Pro, Hy3 via
OpenRouter while free) and stronger models for Assayer/Smith. See
[`docs/MODEL-ROUTING.md`](docs/MODEL-ROUTING.md) and
[`docs/MVP-SETUP.md`](docs/MVP-SETUP.md).

Pipeline workflows still use `anthropics/claude-code-action` by default.
Point them at Anthropic-compatible endpoints (e.g. DeepSeek) or OpenRouter
after secrets are configured — details in the docs above.

---

## How the Automation Works

Same seven-agent pipeline as upstream: discover → triage → extract → review →
synthesize → patrol. Domain filters and feeds are SRE/LLM-ops specific.

Additional references:

- [**DASHBOARD.md**](DASHBOARD.md) — Content health metrics
- [**changelog/**](changelog/) — Weekly summary of guide changes
- [**CONTRADICTIONS.md**](CONTRADICTIONS.md) — Where sources disagree
- [**docs/PROJECT-SETUP.md**](docs/PROJECT-SETUP.md) — GitHub Project board setup
