#!/usr/bin/env python3
"""
Weekly GitHub repo scanner.

Searches for repos with AI agent configuration files (CLAUDE.md, .claude/,
AGENTS.md) and files GitHub issues for new discoveries.

Uses GitHub Search API (code search). Rate limit: 10 requests/minute.

When a NEW repo is discovered (not already in the registry), the scanner
shells out to `gh issue create` so the issue is filed against the
`.github/ISSUE_TEMPLATE/practitioner-repo.yml` template (labels +
structure stay aligned with what humans submit). The registry update
still happens — issue filing is an additional side effect that promotes
the scanner from passive data collector to active driver of Pipeline 1.
"""

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

import scan_budget
import scan_dedup
import _domain

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
REGISTRY_PATH = Path(__file__).parent.parent / "registry" / "repos.json"
REPO_URL = os.environ.get("GITHUB_REPOSITORY", "steveash/hitchhiker-guide")

# Search queries for ops/SRE repos that use AI agent configs or runbooks.
# IMPORTANT (legacy /search/code quirks):
# - Repository qualifiers (stars:, pushed:, fork:) → HTTP 422
# - Parentheses around OR groups → HTTP 422
# Repeat the filename:/path: qualifier on each OR branch instead.
# Star floor is applied in Python after enriching via the repos API.
SEARCH_QUERIES = [
    'filename:AGENTS.md sre OR filename:AGENTS.md runbook OR filename:AGENTS.md oncall OR filename:AGENTS.md incident OR filename:AGENTS.md observability',
    'filename:CLAUDE.md sre OR filename:CLAUDE.md runbook OR filename:CLAUDE.md oncall OR filename:CLAUDE.md incident OR filename:CLAUDE.md pager',
    'path:.claude/settings.json',
    'filename:runbook.md AI OR filename:runbook.md LLM',
    'path:.cursor/rules sre OR path:.cursor/rules oncall OR path:.cursor/rules incident OR path:.cursor/rules platform OR path:.cursor/rules runbook',
]

# Post-filter floor (applied after repo metadata enrich). AGENTS.md adoption
# is recent; keep this low so SRE-relevant repos are not starved.
MIN_STARS = 2

# Repos to always exclude (vendors, tutorials, this fork's owner)
EXCLUDE_OWNERS = {
    'anthropics',
    'steveash',
    'lucas-albers-lz4',
}

# Keywords in repo name/description that suggest it's ABOUT Claude, not USING it
TUTORIAL_KEYWORDS = [
    'awesome-', 'list-of-', 'collection-', 'tutorial', 'guide',
    'template', 'starter', 'boilerplate', 'example-claude',
    'claude-tutorial', 'claude-guide', 'claude-template',
]


def github_headers():
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def search_repos(query: str, page: int = 1) -> tuple[list[dict], str | None]:
    """Search GitHub code API and return (repos, error_message_or_None)."""
    url = "https://api.github.com/search/code"
    params = {"q": query, "per_page": 100, "page": page}
    resp = None
    for attempt in range(4):
        resp = requests.get(url, headers=github_headers(), params=params)
        if resp.status_code not in (403, 429):
            break
        # Prefer Retry-After when present; otherwise escalate wait.
        retry_after = resp.headers.get("Retry-After")
        try:
            wait = int(retry_after) if retry_after else (30 * (attempt + 1))
        except ValueError:
            wait = 30 * (attempt + 1)
        wait = min(max(wait, 15), 120)
        print(
            f"Rate limited ({resp.status_code}), attempt {attempt + 1}/4. "
            f"Waiting {wait}s...",
            file=sys.stderr,
        )
        time.sleep(wait)

    if resp is None or resp.status_code != 200:
        status = resp.status_code if resp is not None else "no-response"
        body_excerpt = ((resp.text if resp is not None else "") or "")[:300].replace(
            "\n", " "
        )
        err = f"HTTP {status}: {body_excerpt}"
        print(f"Search failed for query — {err}", file=sys.stderr)
        return [], err

    data = resp.json()
    repos = {}
    for item in data.get("items", []):
        repo = item["repository"]
        full_name = repo["full_name"]
        if full_name not in repos:
            repos[full_name] = {
                "full_name": full_name,
                "description": repo.get("description", ""),
                "html_url": repo["html_url"],
                # Code-search payloads often omit stargazers_count — enriched below.
                "stars": repo.get("stargazers_count", 0) or 0,
                "config_files_found": [item["path"]],
            }
        else:
            repos[full_name]["config_files_found"].append(item["path"])

    enriched = []
    for repo in repos.values():
        enrich_repo_metadata(repo)
        if repo.get("stars", 0) < MIN_STARS:
            print(
                f"  Below star floor ({repo.get('stars', 0)} < {MIN_STARS}): "
                f"{repo['full_name']}"
            )
            continue
        enriched.append(repo)

    return enriched, None


def enrich_repo_metadata(repo: dict) -> None:
    """Fill stars/description from GET /repos/{full_name} when missing."""
    full_name = repo["full_name"]
    if repo.get("stars") and repo.get("description"):
        return
    try:
        resp = requests.get(
            f"https://api.github.com/repos/{full_name}",
            headers=github_headers(),
            timeout=30,
        )
        if resp.status_code != 200:
            return
        data = resp.json()
        repo["stars"] = data.get("stargazers_count", repo.get("stars", 0)) or 0
        if not repo.get("description"):
            repo["description"] = data.get("description") or ""
        # Prefer canonical html_url
        if data.get("html_url"):
            repo["html_url"] = data["html_url"]
    except requests.RequestException as e:
        print(f"  WARN: could not enrich {full_name}: {e}", file=sys.stderr)


def is_excluded(repo: dict) -> bool:
    """Check if repo should be excluded based on heuristics."""
    full_name = repo["full_name"]
    owner = full_name.split("/")[0]
    name = full_name.split("/")[1].lower()
    desc = (repo.get("description") or "").lower()

    if owner in EXCLUDE_OWNERS:
        return True

    for kw in TUTORIAL_KEYWORDS:
        if kw in name or kw in desc:
            return True

    # Pure coding-agent DX with no SRE/LLM-ops signal (config flag).
    if not _domain.is_sre_relevant(f"{name} {desc}"):
        return True

    return False


def load_registry() -> dict:
    """Load existing repo registry."""
    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH) as f:
            return json.load(f)
    return {"repos": {}, "last_scan": None}


def save_registry(registry: dict):
    """Save repo registry."""
    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(REGISTRY_PATH, "w") as f:
        json.dump(registry, f, indent=2, default=str)


def file_issue(repo: dict, is_update: bool = False) -> bool:
    """File a GitHub issue for a discovered repo via `gh issue create`.

    Body and labels are aligned with `.github/ISSUE_TEMPLATE/practitioner-repo.yml`
    so auto-filed issues look like the human-submitted ones and flow through the
    same triage path. Uses `gh` (not the raw REST API) so authentication picks up
    GH_TOKEN/GITHUB_TOKEN from the environment in CI and from the user's local
    `gh auth login` when run by hand.

    Returns True on successful filing, False otherwise. The boolean lets the
    caller decide whether to count the file against the daily-cap budget.
    """
    if shutil.which("gh") is None:
        print(
            "  ERROR: `gh` CLI not found — cannot file issue. "
            "Install GitHub CLI or run inside the GitHub Actions workflow.",
            file=sys.stderr,
        )
        return False

    label = "repo-updated" if is_update else "new-repo"
    title_prefix = "[repo-update]" if is_update else "[repo]"
    title = f'{title_prefix} {repo["full_name"]}'

    config_files = repo.get("config_files_found", [])
    config_files_md = (
        "\n".join(f"- `{f}`" for f in config_files) if config_files else "- (none detected)"
    )

    relevance_blob = f"{repo.get('full_name', '')} {repo.get('description') or ''}"
    relevance = _domain.domain_relevance(relevance_blob)

    # Body mirrors the practitioner-repo.yml form sections so triage tooling can
    # treat auto-filed and human-filed issues the same way.
    body = f"""### Repository

{repo['full_name']}

URL: {repo['html_url']}

### AI config files present

{config_files_md}

### What operational/SRE pattern does this repo demonstrate?

Auto-discovered by the repo scanner. Prospector: pick the best fit —

- Operational runbook content (incident response, oncall, SLOs, postmortems)
- AI agent usage patterns (which AI tools are wired in ops, and how)
- Observability + LLM tracing patterns (OTel GenAI, LLM evals)
- Production safety patterns (eval gates, cost monitors, prompt/version mgmt)

Note: CLAUDE.md / `.cursorrules` / AGENTS.md are evidence of AI agent adoption
in production, not the primary classification.

### What makes this repo worth analyzing?

Auto-discovered by the weekly repo scanner.

- Stars: {repo.get('stars', 'unknown')}
- Description: {repo.get('description') or 'No description'}
- **domain_relevance**: {relevance}

This issue was filed automatically and needs triage by the Prospector agent.

---
*Filed by `scripts/scan-repos.py` against `.github/ISSUE_TEMPLATE/practitioner-repo.yml`*
"""

    cmd = [
        "gh", "issue", "create",
        "--repo", REPO_URL,
        "--title", title,
        "--body", body,
        "--label", label,
        "--label", "practitioner-repo",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        url_out = result.stdout.strip()
        print(f"  Filed issue for {repo['full_name']}: {url_out}")
        return True
    except subprocess.CalledProcessError as e:
        print(
            f"  Failed to file issue for {repo['full_name']} "
            f"(exit {e.returncode}): {e.stderr.strip()}",
            file=sys.stderr,
        )
        return False


def drain_queue(dry_run: bool = False) -> int:
    """File repo entries previously queued by this scanner. Returns count filed."""
    budget = scan_budget.remaining()
    if budget <= 0:
        return 0
    queued_items = scan_budget.pop_queued_for("repos", budget)
    if not queued_items:
        return 0
    print(f"Draining {len(queued_items)} queued repo item(s) from prior runs...")
    filed = 0
    for item in queued_items:
        payload = item.get("payload", {})
        repo = payload.get("repo")
        is_update = payload.get("is_update", False)
        if not repo:
            print(f"  WARN: skipping malformed queue item: {item}", file=sys.stderr)
            continue
        if scan_dedup.is_url_already_tracked(repo.get("html_url", "")):
            print(f"  [dedup] already tracked (queued): {repo.get('full_name', '')}")
            continue
        if dry_run:
            print(f"  [DRY-RUN] would file (queued): {repo.get('full_name', '')}")
            filed += 1
            continue
        if file_issue(repo, is_update=is_update):
            filed += 1
            scan_budget.record_filed(1)
    return filed


def _try_file_or_queue(repo: dict, is_update: bool, dry_run: bool = False) -> tuple[bool, bool]:
    """File a repo issue if budget allows, otherwise queue it for next run.

    Returns (filed, queued) — exactly one will be True. The repo is
    *always* recorded as known in the registry afterwards (caller's
    responsibility) so we never re-discover it tomorrow; the queue is now
    the canonical home for the unfiled work.
    """
    if not dry_run and scan_dedup.is_url_already_tracked(repo.get("html_url", "")):
        print(f"  [dedup] already tracked: {repo['full_name']}")
        return (False, False)
    if dry_run:
        print(f"  [DRY-RUN] would file: {repo['full_name']}")
        return (True, False)
    if scan_budget.remaining() <= 0:
        scan_budget.queue_item("repos", {"repo": repo, "is_update": is_update})
        print(f"  [queued] daily cap reached: {repo['full_name']}")
        return (False, True)
    if file_issue(repo, is_update=is_update):
        scan_budget.record_filed(1)
        return (True, False)
    return (False, False)


def main():
    parser = argparse.ArgumentParser(description="Scan GitHub for SRE/ops repos with AI agent configs.")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Search and report NEW/Excluded/summary without filing issues or writing registry.",
    )
    args = parser.parse_args()

    registry = load_registry()
    known_repos = registry.get("repos", {})
    all_discovered = {}

    print(f"scan-repos starting: {scan_budget.status_summary()}")

    # Drain repo backlog from prior runs first so the oldest discoveries
    # become Pipeline 1 issues before we go looking for fresh ones.
    drained = drain_queue(dry_run=args.dry_run)
    if drained:
        print(f"Refiled {drained} item(s) from queue. {scan_budget.status_summary()}")

    print("Starting repo scan...")

    queries_run = 0
    query_failures = 0
    raw_hits = 0

    for query in SEARCH_QUERIES:
        queries_run += 1
        print(f"\nSearching: {query}")
        repos, err = search_repos(query)
        if err:
            query_failures += 1
            print(f"  Query error — treating as 0 results ({err})", file=sys.stderr)
        print(f"  Found {len(repos)} repos")
        raw_hits += len(repos)

        for repo in repos:
            name = repo["full_name"]
            if name not in all_discovered:
                all_discovered[name] = repo
            else:
                # Merge config files lists
                existing_files = all_discovered[name]["config_files_found"]
                new_files = repo["config_files_found"]
                all_discovered[name]["config_files_found"] = list(
                    set(existing_files + new_files)
                )

        # Code search secondary rate limit — stay under ~30 req/min.
        time.sleep(12)

    # Filter and process
    new_count = 0
    update_count = 0
    queued_count = 0
    excluded_count = 0
    skipped_count = 0

    for name, repo in all_discovered.items():
        if is_excluded(repo):
            print(f"  Excluded: {name}")
            excluded_count += 1
            continue

        if name not in known_repos:
            print(f"  NEW: {name}")
            filed, queued = _try_file_or_queue(repo, is_update=False, dry_run=args.dry_run)
            if not args.dry_run:
                known_repos[name] = {
                    "first_seen": datetime.now(timezone.utc).isoformat(),
                    "last_scanned": datetime.now(timezone.utc).isoformat(),
                    "config_files": repo["config_files_found"],
                    "stars": repo.get("stars", 0),
                }
            if filed:
                new_count += 1
            elif queued:
                queued_count += 1
            else:
                skipped_count += 1
        else:
            # Check if config files changed
            old_files = set(known_repos[name].get("config_files", []))
            new_files = set(repo["config_files_found"])
            if new_files != old_files:
                print(f"  UPDATED: {name} (config files changed)")
                filed, queued = _try_file_or_queue(repo, is_update=True, dry_run=args.dry_run)
                if not args.dry_run:
                    known_repos[name]["last_scanned"] = datetime.now(timezone.utc).isoformat()
                    known_repos[name]["config_files"] = repo["config_files_found"]
                if filed:
                    update_count += 1
                elif queued:
                    queued_count += 1
                else:
                    skipped_count += 1
            elif not args.dry_run:
                known_repos[name]["last_scanned"] = datetime.now(timezone.utc).isoformat()

    if not args.dry_run:
        registry["repos"] = known_repos
        registry["last_scan"] = datetime.now(timezone.utc).isoformat()
        save_registry(registry)

    filed_total = new_count + update_count
    print(
        f"\nScan complete: queries={queries_run} found={len(all_discovered)} "
        f"(raw_hits={raw_hits}) excluded={excluded_count} filed={filed_total} "
        f"(new={new_count} updated={update_count}) queued={queued_count} "
        f"skipped={skipped_count} query_failures={query_failures} "
        f"tracked={len(known_repos)}"
    )
    print(f"Final budget: {scan_budget.status_summary()}")


if __name__ == "__main__":
    main()
