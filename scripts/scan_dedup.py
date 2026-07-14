"""
Deterministic URL / repo deduplication for discovery scanners.

Before filing a new issue, scanners call:

* `is_url_already_tracked(url)` — source-notes `source_url:` + open issue bodies
* `is_repo_already_tracked(full_name)` — open **or closed** issue titles matching
  `[repo] full_name` / `[repo-update] full_name` (guards concurrent daily-scan races
  and prevents refiling after a prior run closed a duplicate)

This is a cheap grep + API call — no LLM involved.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_NOTES_DIR = Path(__file__).parent.parent / "source-notes"
REPO_URL = os.environ.get("GITHUB_REPOSITORY", "steveash/hitchhiker-guide")

# Caches — populated once per process on first call.
_source_notes_urls: set[str] | None = None
_open_issue_bodies: list[str] | None = None
_repo_issue_titles: set[str] | None = None


def _load_source_notes_urls() -> set[str]:
    """Read source_url: frontmatter from all source-notes/*.md files."""
    global _source_notes_urls
    if _source_notes_urls is not None:
        return _source_notes_urls

    urls: set[str] = set()
    if not SOURCE_NOTES_DIR.is_dir():
        _source_notes_urls = urls
        return urls

    for md_file in SOURCE_NOTES_DIR.glob("*.md"):
        try:
            with open(md_file) as f:
                in_frontmatter = False
                for line in f:
                    stripped = line.strip()
                    if stripped == "---":
                        if in_frontmatter:
                            break  # end of frontmatter
                        in_frontmatter = True
                        continue
                    if in_frontmatter and stripped.startswith("source_url:"):
                        url = stripped.split(":", 1)[1].strip()
                        if url:
                            urls.add(url)
                        break
        except OSError:
            continue

    _source_notes_urls = urls
    return urls


def _load_open_issue_bodies() -> list[str]:
    """Fetch bodies of all open issues via gh CLI (cached per process)."""
    global _open_issue_bodies
    if _open_issue_bodies is not None:
        return _open_issue_bodies

    _open_issue_bodies = []
    if shutil.which("gh") is None:
        return _open_issue_bodies

    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", REPO_URL,
                "--state", "open",
                "--json", "body",
                "--limit", "500",
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if result.returncode == 0:
            issues = json.loads(result.stdout)
            _open_issue_bodies = [
                issue.get("body", "") for issue in issues
            ]
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"  WARN: could not fetch open issues for dedup: {e}", file=sys.stderr)

    return _open_issue_bodies


def _load_repo_issue_titles() -> set[str]:
    """Titles of `[repo]` / `[repo-update]` issues in any state (cached)."""
    global _repo_issue_titles
    if _repo_issue_titles is not None:
        return _repo_issue_titles

    _repo_issue_titles = set()
    if shutil.which("gh") is None:
        return _repo_issue_titles

    try:
        # Include closed: concurrent runs may have filed then pre-screen-closed
        # duplicates; we must not refile the same full_name again.
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--repo", REPO_URL,
                "--state", "all",
                "--search", 'in:title "[repo]"',
                "--json", "title",
                "--limit", "500",
            ],
            capture_output=True,
            text=True,
            timeout=90,
        )
        if result.returncode == 0:
            for issue in json.loads(result.stdout):
                title = (issue.get("title") or "").strip()
                if title.startswith("[repo]") or title.startswith("[repo-update]"):
                    _repo_issue_titles.add(title)
    except (subprocess.TimeoutExpired, subprocess.SubprocessError, json.JSONDecodeError) as e:
        print(f"  WARN: could not fetch repo issue titles for dedup: {e}", file=sys.stderr)

    return _repo_issue_titles


def is_url_already_tracked(url: str) -> bool:
    """Check if a URL is already tracked in source-notes or open issues.

    Returns True if the URL should be skipped (already known).
    """
    if not url:
        return False

    # Check 1: source-notes frontmatter (local, instant)
    if url in _load_source_notes_urls():
        return True

    # Check 2: open GitHub issue bodies (cached API call)
    for body in _load_open_issue_bodies():
        if url in body:
            return True

    return False


def is_repo_already_tracked(full_name: str) -> bool:
    """True if a `[repo]` / `[repo-update]` issue already exists for this full_name.

    Checks open and closed issue titles so a prior run's closed duplicate still
    blocks refiling (ledger race during concurrent daily-scan).
    """
    if not full_name:
        return False

    name = full_name.strip()
    candidates = (
        f"[repo] {name}",
        f"[repo-update] {name}",
    )
    titles = _load_repo_issue_titles()
    return any(t in titles for t in candidates)
