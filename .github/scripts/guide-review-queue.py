#!/usr/bin/env python3
"""Refresh the single durable review queue for open guide-update PRs."""

from datetime import datetime, timezone
import json
import os
import re
import subprocess
import tempfile

REPO = os.environ["GITHUB_REPOSITORY"]
STALE_DAYS = int(os.environ.get("STALE_DAYS", "14"))
MARKER = "<!-- guide-update-review-queue -->"


def gh(*args):
    result = subprocess.run(["gh", *args], check=True, text=True, capture_output=True)
    return result.stdout


def api(path):
    return json.loads(gh("api", path))


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def latest_assayer(comments):
    findings = []
    for comment in comments:
        body = comment.get("body", "")
        sha = re.search(r"<!-- assayer-verdict: sha=([0-9a-f]+) -->", body)
        verdict = re.search(r"\*\*Verdict\*\*:\s*([^\n]+)", body)
        if sha and verdict:
            findings.append((comment["created_at"], verdict.group(1).strip(), sha.group(1)))
    return max(findings, default=None, key=lambda item: item[0])


def main():
    now = datetime.now(timezone.utc)
    pulls = api(f"repos/{REPO}/pulls?state=open&per_page=100")
    guide_prs = [p for p in pulls if any(l["name"] == "guide-update" for l in p["labels"])]
    guide_prs.sort(key=lambda p: (p["updated_at"], p["number"]))

    rows = []
    stale = []
    for pr in guide_prs:
        number = pr["number"]
        comments = api(f"repos/{REPO}/issues/{number}/comments?per_page=100")
        reviews = api(f"repos/{REPO}/pulls/{number}/reviews?per_page=100")
        verdict = latest_assayer(comments)
        head = pr["head"]["sha"]
        if verdict is None:
            assayer = "No verdict found"
            verdict_sha = "—"
            fresh = "unknown"
        else:
            created, value, verdict_sha = verdict
            fresh = "current" if verdict_sha == head else "STALE SHA"
            assayer = f"{value} ({fresh}; {created[:10]})"

        human_reviews = [r for r in reviews
                         if r.get("state") in {"APPROVED", "CHANGES_REQUESTED", "COMMENTED"}
                         and r.get("user", {}).get("type") != "Bot"
                         and not r.get("user", {}).get("login", "").endswith("[bot]")]
        latest_human = max(human_reviews, default=None, key=lambda r: r.get("submitted_at") or "")
        human = (f"{latest_human['state']} by @{latest_human['user']['login']}"
                 if latest_human else "No human review")
        days = (now - parse_time(pr["updated_at"])).days
        comparison = api(f"repos/{REPO}/compare/main...{head}")
        behind = comparison.get("behind_by", 0)
        stale_reasons = []
        if days >= STALE_DAYS:
            stale_reasons.append(f"{days}d since update")
        if behind >= 25:
            stale_reasons.append(f"{behind} commits behind main")
        stale_label = f" **STALE ({'; '.join(stale_reasons)})**" if stale_reasons else ""
        title = pr["title"].replace("|", "\\|")
        rows.append(
            f"| [#{number}]({pr['html_url']}) | {title} | "
            f"`{head[:12]}` | {assayer} | {human} | {days}d / {behind} behind{stale_label} |"
        )
        if stale_reasons:
            stale.append(f"- [#{number}]({pr['html_url']}) — {', '.join(stale_reasons)}")

    updated = now.strftime("%Y-%m-%d %H:%M UTC")
    body = [MARKER, "# Guide-update PR review queue", "",
            f"Updated automatically: {updated}. Stale thresholds: **{STALE_DAYS} days** since update or **25 commits** behind `main`.",
            "Assayer verdict freshness is determined by matching its recorded head SHA to the current PR head.", "",
            "| PR | Title | Current head SHA | Latest Assayer verdict | Latest human review | Updated / behind main |",
            "|---|---|---|---|---|---:|"]
    body.extend(rows or ["| — | No open `guide-update` PRs | — | — | — | — |"])
    body.extend(["", "## Stale PRs", ""])
    body.extend(stale or ["None."])
    body.extend(["", "## Review guidance", "",
                 "For each open guide update, verify the Assayer verdict is current for the displayed head SHA, then obtain human review. "
                 "For overlapping chapter edits, decide whether to merge in order, rebase, or close/supersede a PR. "
                 "This queue is informational; it does not approve or merge PRs.", ""])
    rendered = "\n".join(body)

    issues = api(f"repos/{REPO}/issues?state=open&per_page=100")
    queue = next((i for i in issues if MARKER in (i.get("body") or "")), None)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8") as f:
        f.write(rendered)
        f.flush()
        if queue:
            gh("issue", "edit", str(queue["number"]), "--body-file", f.name)
            print(f"Updated review queue issue #{queue['number']}.")
        else:
            # no-triage prevents the source-submission pipeline from consuming this tooling issue.
            gh("issue", "create", "--title", "Guide-update PR review queue", "--label", "no-triage",
               "--body-file", f.name)
            print("Created review queue issue.")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a", encoding="utf-8") as f:
            f.write(rendered.replace(MARKER, ""))


if __name__ == "__main__":
    main()
