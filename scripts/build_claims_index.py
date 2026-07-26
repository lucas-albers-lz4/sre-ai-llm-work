#!/usr/bin/env python3
"""Regenerate registry/claims-index.json from source-note claim headings.

Derived index for Miner cross-reference retrieval (#506). Never hand-edit.
Rebuilds at Miner job start from checkout and via registry-rebuild.yml.

Usage:
  python3 scripts/build_claims_index.py            # rewrite registry/claims-index.json
  python3 scripts/build_claims_index.py --check     # exit 1 if out of date (CI guard)

Index surface per note: title, source_url, Guide Impact chapter refs, and
claim/pattern/lesson headings. Author/publisher omitted (MVP).
"""
from __future__ import annotations

import glob
import json
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTES_DIR = os.path.join(ROOT, "source-notes")
REGISTRY = os.path.join(ROOT, "registry", "claims-index.json")

CLAIM_HEADING_RE = re.compile(
    r"^###\s+(?P<kind>Claim|Pattern|Lesson)"
    r"(?:\s+(?P<n>\d+))?"
    r"(?:\s*:\s*(?P<title>.*))?$",
    re.MULTILINE | re.IGNORECASE,
)
GUIDE_IMPACT_RE = re.compile(
    r"^##\s+Guide Impact\s*$",
    re.MULTILINE | re.IGNORECASE,
)
CHAPTER_RE = re.compile(
    r"\*\*Chapter\s+(\d{2})\b[^:]*\*\*",
    re.IGNORECASE,
)
NEXT_H2_RE = re.compile(r"^##\s+\S", re.MULTILINE)


def _line_parse(block: str) -> dict:
    """Fallback flat parser for front-matter that isn't valid YAML."""
    out = {}
    for line in block.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        m = re.match(r"^([A-Za-z_][\w-]*):\s?(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
            val = val[1:-1]
        out[key] = val
    return out


def parse_front_matter(text: str) -> dict | None:
    """Return the front-matter dict for note text, or None if absent."""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    block = text[3:end]
    try:
        loaded = yaml.safe_load(block)
        if isinstance(loaded, dict):
            return loaded
    except yaml.YAMLError:
        pass
    return _line_parse(block)


def extract_chapters(text: str) -> list[str]:
    """Chapter ids from ## Guide Impact (e.g. '02', '04')."""
    m = GUIDE_IMPACT_RE.search(text)
    if not m:
        return []
    start = m.end()
    nxt = NEXT_H2_RE.search(text, start)
    section = text[start : nxt.start() if nxt else len(text)]
    seen = []
    for ch in CHAPTER_RE.findall(section):
        if ch not in seen:
            seen.append(ch)
    return seen


def extract_claims(text: str) -> list[dict]:
    """Claim/pattern/lesson headings in document order."""
    claims = []
    pattern_seq = 0
    for m in CLAIM_HEADING_RE.finditer(text):
        kind = m.group("kind").lower()
        raw_n = m.group("n")
        title = (m.group("title") or "").strip()
        if kind == "pattern" and raw_n is None:
            pattern_seq += 1
            n = pattern_seq
        elif raw_n is not None:
            n = int(raw_n)
        else:
            n = len(claims) + 1
        heading = title if title else f"{m.group('kind')} {n}"
        claims.append({"n": n, "heading": heading, "kind": kind})
    return claims


def should_skip_slug(slug: str) -> bool:
    if slug.startswith("."):
        return True
    if slug.endswith("-eval") or slug.endswith("-hy3-eval"):
        return True
    return False


def build() -> dict:
    notes = {}
    for path in sorted(glob.glob(os.path.join(NOTES_DIR, "*.md"))):
        slug = os.path.basename(path)[:-3]
        if should_skip_slug(slug):
            continue
        with open(path, encoding="utf-8") as f:
            text = f.read()
        fm = parse_front_matter(text) or {}
        title = fm.get("title")
        if title is not None and not isinstance(title, str):
            title = str(title)
        source_url = fm.get("source_url")
        if source_url is not None and not isinstance(source_url, str):
            source_url = str(source_url)
        entry = {
            "path": f"source-notes/{slug}.md",
            "title": title or slug,
            "source_url": source_url or "",
            "chapters": extract_chapters(text),
            "claims": extract_claims(text),
        }
        notes[slug] = entry
    return {"version": 1, "notes": notes}


def main() -> int:
    check = "--check" in sys.argv
    new = build()
    new_text = json.dumps(new, indent=2, ensure_ascii=False) + "\n"
    if check:
        try:
            cur = open(REGISTRY, encoding="utf-8").read()
        except FileNotFoundError:
            cur = ""
        if cur != new_text:
            print(
                "registry/claims-index.json is OUT OF DATE — "
                "run scripts/build_claims_index.py",
                file=sys.stderr,
            )
            return 1
        print("registry/claims-index.json is up to date.")
        return 0
    os.makedirs(os.path.dirname(REGISTRY), exist_ok=True)
    with open(REGISTRY, "w", encoding="utf-8") as f:
        f.write(new_text)
    print(f"Wrote {REGISTRY} with {len(new['notes'])} notes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
