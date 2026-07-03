# Weekly Guide Changelog

This directory holds one changelog report per week that saw guide changes.
Each report is an executive summary of the `guide/*.md` edits that landed that
week — what changed, and why it matters to a reader following the guide.

## File naming

One file per change-week, named by ISO week:

```
YYYY-Www.md      e.g. 2026-W27.md
```

**Quiet weeks produce no file.** If nothing in `guide/` changed, the chain
simply extends to the next report that does land (see below).

## Front-matter schema

Every report begins with YAML front matter:

```yaml
---
week: 2026-W27                 # ISO week this report covers
generated: 2026-07-06T09:00Z   # UTC timestamp the report was produced
from_commit: <sha>             # exclusive lower bound of the diff range
to_commit: <sha>               # inclusive upper bound (origin/main HEAD)
guide_files_changed:           # guide/*.md files touched in the range
  - guide/02-harness-engineering.md
  - guide/03-verification.md
---
```

## The chaining contract

Reports form an unbroken chain over commit history:

- `from_commit` of each report **equals the `to_commit` of the previous
  report**.
- `to_commit` is `origin/main` HEAD at generation time.

This is **self-healing**: if a week is missed (workflow skipped, outage), the
next report's range widens automatically to start from the last report's
`to_commit`, so no guide change is ever dropped from the chain.

Because of this, the `to_commit` fields are **load-bearing**. Do not hand-edit
reports — a wrong `to_commit` breaks the next report's starting point and can
silently skip changes.

## How reports are generated

Reports are produced by the **Herald** workflow
(`.github/workflows/herald-weekly.yml`), which runs on a weekly schedule per
`agents/HERALD.md`. For each change-week, Herald also cuts a
`guide-YYYY-MM-DD` GitHub Release marking the guide's state at that point.

Herald owns this directory. Treat every file here as generated output.
