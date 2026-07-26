#!/usr/bin/env python3
"""Lexical related-note retrieval for Miner cross-reference candidates (#506).

Reads registry/claims-index.json, ranks notes by token overlap + same-URL
bonus, always includes every note with a normalized matching source_url,
and writes a Markdown candidate list for prompt injection.

Usage:
  python3 scripts/related_notes.py \\
    --issue-title '...' \\
    --source-url 'https://...' \\
    --body-file /tmp/issue-body.txt \\
    --out "${RUNNER_TEMP}/miner-related-notes.md"

  # or --body 'excerpt...' instead of --body-file

Env/stdout labeling:
  Writes HAS_CANDIDATES=true|false to GITHUB_OUTPUT when set (Actions).
  Also prints HAS_CANDIDATES=... on stderr for local debugging.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_INDEX = os.path.join(ROOT, "registry", "claims-index.json")

STOPWORDS = frozenset(
    """
    a an the and or but if in on at to for of from with by as is are was were
    be been being this that these those it its their our your you we they he
    she him her them not no nor so than then too very can could should would
    will just about into over after before under again further once here there
    when where why how all each few more most other some such only own same
    """.split()
)

TOKEN_RE = re.compile(r"[a-z0-9]+")
URL_IN_TEXT_RE = re.compile(r"https?://[^\s)>\]]+", re.IGNORECASE)


def tokenize(text: str) -> set[str]:
    tokens = set()
    for t in TOKEN_RE.findall((text or "").lower()):
        if len(t) < 3 or t in STOPWORDS:
            continue
        tokens.add(t)
    return tokens


def normalize_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip()
    try:
        parts = urlsplit(url)
    except ValueError:
        return url.rstrip("/").lower()
    scheme = parts.scheme.lower()
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or ""
    # Drop utm_* and empty query noise; keep other query keys stable.
    q = [
        (k, v)
        for k, v in parse_qsl(parts.query, keep_blank_values=True)
        if not k.lower().startswith("utm_")
    ]
    query = urlencode(q)
    return urlunsplit((scheme, netloc, path, query, ""))  # no fragment


def note_tokens(entry: dict) -> set[str]:
    parts = [entry.get("title") or ""]
    parts.extend(entry.get("chapters") or [])
    for c in entry.get("claims") or []:
        parts.append(c.get("heading") or "")
    return tokenize(" ".join(parts))


def extract_source_url_from_body(body: str) -> str:
    """Best-effort: first URL after 'Source URL' heading, else first http URL."""
    if not body:
        return ""
    m = re.search(
        r"(?i)source\s*url\s*\n+\s*(https?://\S+)",
        body,
    )
    if m:
        return m.group(1).rstrip(").,]")
    m = URL_IN_TEXT_RE.search(body)
    return m.group(0).rstrip(").,]") if m else ""


def score_note(
    query_tokens: set[str],
    entry: dict,
    query_url_norm: str,
) -> tuple[float, bool]:
    bag = note_tokens(entry)
    if not query_tokens:
        overlap = 0.0
    else:
        overlap = len(query_tokens & bag) / len(query_tokens)
    same_url = bool(
        query_url_norm and normalize_url(entry.get("source_url") or "") == query_url_norm
    )
    score = overlap + (2.0 if same_url else 0.0)
    return score, same_url


def rank(
    index: dict,
    title: str,
    source_url: str,
    body: str,
    top_n: int,
) -> list[tuple[str, dict, float, bool]]:
    body_excerpt = (body or "")[:500]
    query_url = normalize_url(source_url) if source_url else ""
    if not query_url:
        query_url = normalize_url(extract_source_url_from_body(body))
    query_parts = [title or "", body_excerpt]
    if source_url:
        query_parts.append(source_url)
    q_tokens = tokenize(" ".join(query_parts))

    forced: list[tuple[str, dict, float, bool]] = []
    scored: list[tuple[str, dict, float, bool]] = []
    for slug, entry in (index.get("notes") or {}).items():
        path = entry.get("path") or f"source-notes/{slug}.md"
        abs_path = os.path.join(ROOT, path)
        if not os.path.isfile(abs_path):
            print(f"WARN: dropping phantom path {path}", file=sys.stderr)
            continue
        s, same = score_note(q_tokens, entry, query_url)
        row = (slug, entry, s, same)
        if same:
            forced.append(row)
        else:
            scored.append(row)

    scored.sort(key=lambda r: (-r[2], -len(r[1].get("claims") or []), r[0]))
    forced.sort(key=lambda r: (-r[2], -len(r[1].get("claims") or []), r[0]))

    # Always include all same-URL notes, then fill to top_n.
    chosen = list(forced)
    seen = {r[0] for r in chosen}
    for row in scored:
        if len(chosen) >= top_n:
            break
        if row[0] in seen:
            continue
        chosen.append(row)
        seen.add(row[0])
    # If forced alone exceeds top_n, keep all forced (same-URL is mandatory).
    return chosen


def render_markdown(rows: list[tuple[str, dict, float, bool]]) -> str:
    lines = [
        "# Related source-note candidates",
        "",
        "Deterministic lexical retrieval for Miner cross-references.",
        "Candidates are suggestions only — cite or explicitly dismiss each",
        "before writing Cross-References. Still verify every citation (§4b).",
        "",
    ]
    if not rows:
        lines.append("_No candidates found._")
        lines.append("")
        return "\n".join(lines)

    for i, (slug, entry, score, same) in enumerate(rows, 1):
        path = entry.get("path") or f"source-notes/{slug}.md"
        title = entry.get("title") or slug
        url = entry.get("source_url") or "(none)"
        tag = " same-url" if same else ""
        lines.append(f"## {i}. `{path}`{tag}")
        lines.append(f"- **title**: {title}")
        lines.append(f"- **source_url**: {url}")
        lines.append(f"- **score**: {score:.4f}")
        claims = entry.get("claims") or []
        if claims:
            lines.append("- **matching claim one-liners** (up to 5):")
            for c in claims[:5]:
                kind = c.get("kind") or "claim"
                n = c.get("n")
                heading = c.get("heading") or ""
                lines.append(f"  - {kind.title()} {n}: {heading}")
        else:
            lines.append("- **matching claim one-liners**: _(none indexed)_")
        lines.append("")
    return "\n".join(lines)


def write_github_output(has_candidates: bool) -> None:
    val = "true" if has_candidates else "false"
    print(f"HAS_CANDIDATES={val}", file=sys.stderr)
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as f:
            f.write(f"has_candidates={val}\n")
            f.write("ran_candidates=true\n")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--issue-title", default="", help="Issue title")
    p.add_argument("--source-url", default="", help="Source URL if known")
    p.add_argument("--body", default="", help="Issue body (or excerpt)")
    p.add_argument("--body-file", default="", help="Read issue body from file")
    p.add_argument("--index", default=DEFAULT_INDEX, help="claims-index.json path")
    p.add_argument("--out", required=True, help="Markdown output path")
    p.add_argument("--top-n", type=int, default=10, help="Max candidates (default 10)")
    args = p.parse_args(argv)

    body = args.body
    if args.body_file:
        with open(args.body_file, encoding="utf-8") as f:
            body = f.read()

    with open(args.index, encoding="utf-8") as f:
        index = json.load(f)

    rows = rank(index, args.issue_title, args.source_url, body, args.top_n)
    md = render_markdown(rows)
    out_dir = os.path.dirname(args.out)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(md)

    write_github_output(bool(rows))
    print(f"Wrote {args.out} with {len(rows)} candidates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
