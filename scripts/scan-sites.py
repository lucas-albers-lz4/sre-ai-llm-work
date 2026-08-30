#!/usr/bin/env python3
"""
Site-crawl scanner: seed-based documentation site discovery.

Given a curated list of "seed" URLs (documentation sites, knowledge bases),
this scanner discovers pages via sitemap.xml or nav-link extraction, screens
them for relevance using a fast DeepSeek Flash LLM call, and files GitHub issues for
relevant pages to feed into the existing source pipeline.

Per-seed crawl state lives in `registry/site-crawl-state.json` so the
hand-edited seed list stays diff-clean across runs.

URL lifecycle in state:
  (not in state) → discovered → screened:pending | screened:rejected
  screened:pending → filed

Runs as a step in the daily-scan workflow alongside feed/failure scanners.
Shares the same daily-cap budget via scan_budget.
"""

import argparse
import json
import os
import re
import subprocess
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

import scan_budget
import scan_dedup

GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
ANTHROPIC_BASE_URL = os.environ.get(
    "ANTHROPIC_BASE_URL", "https://api.deepseek.com/anthropic"
).rstrip("/")
# When pointed at OpenRouter, prefer OR tokens so a co-present DEEPSEEK_API_KEY
# cannot override the OR arm of an A/B run.
if "openrouter.ai" in ANTHROPIC_BASE_URL:
    ANTHROPIC_API_KEY = (
        os.environ.get("ANTHROPIC_AUTH_TOKEN")
        or os.environ.get("OPENROUTER_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("DEEPSEEK_API_KEY")
    )
else:
    ANTHROPIC_API_KEY = (
        os.environ.get("DEEPSEEK_API_KEY")
        or os.environ.get("ANTHROPIC_API_KEY")
        or os.environ.get("ANTHROPIC_AUTH_TOKEN")
    )
SCREEN_MODEL = os.environ.get("SITE_CRAWL_MODEL", "deepseek-v4-flash")
# Optional OpenRouter provider prefs JSON, e.g.
# {"quantizations":["fp8"],"allow_fallbacks":false,"only":["DeepInfra"]}
# Empty / unset → omit provider object (DeepSeek direct / default OR routing).
SITE_CRAWL_PROVIDER_JSON = os.environ.get("SITE_CRAWL_PROVIDER_JSON", "").strip()
REPO_URL = os.environ.get("GITHUB_REPOSITORY", "steveash/hitchhiker-guide")

SEEDS_PATH = Path(__file__).parent.parent / "registry" / "site-crawl-seeds.json"
STATE_PATH = Path(__file__).parent.parent / "registry" / "site-crawl-state.json"

USER_AGENT = "hitchhiker-guide-site-crawler/1.0 (+https://github.com/steveash/hitchhiker-guide)"
REQUEST_TIMEOUT = 30
INTER_REQUEST_SLEEP = 1  # seconds between requests (be polite)

# Max issues to file per run across all seeds.
MAX_ISSUES_PER_RUN = 20

# Default max new URLs to screen/file per seed per run (overridable via seed.max_per_run).
DEFAULT_MAX_PER_RUN = 3

# Legacy hard ceiling on screening if a seed omits max_per_run and someone
# raises DEFAULT — keep Flash API costs bounded.
MAX_SCREEN_PER_SEED = 50

# Accumulated Flash API usage for SITE_CRAWL_USAGE_TOTAL (reset each run).
_usage_run_totals: dict[str, int] = {
    "calls": 0,
    "errors": 0,
    "input_tokens": 0,
    "output_tokens": 0,
    "cache_read": 0,
    "cache_miss": 0,
    "cache_creation": 0,
    "unparsed_urls": 0,
}


def _reset_usage_run_totals() -> None:
    for key in _usage_run_totals:
        _usage_run_totals[key] = 0


def _usage_from_response(result: dict) -> dict[str, int]:
    """Normalize Messages API usage (Anthropic + DeepSeek + OR field aliases)."""
    usage = result.get("usage") or {}

    def pick(*keys: str) -> int:
        for key in keys:
            val = usage.get(key)
            if val is not None:
                return int(val)
        return 0

    # Nested Anthropic-style cache details (some OR hosts).
    cache_read_details = 0
    details = usage.get("prompt_tokens_details") or usage.get("input_tokens_details")
    if isinstance(details, dict):
        for key in ("cached_tokens", "cache_read_input_tokens", "prompt_cache_hit_tokens"):
            if details.get(key) is not None:
                cache_read_details = int(details[key])
                break

    cache_read = pick("prompt_cache_hit_tokens", "cache_read_input_tokens")
    if cache_read == 0 and cache_read_details:
        cache_read = cache_read_details

    return {
        "input_tokens": pick("input_tokens", "prompt_tokens"),
        "output_tokens": pick("output_tokens", "completion_tokens"),
        # Prefer DeepSeek console names on this client; Anthropic names second.
        "cache_read": cache_read,
        # DeepSeek miss = uncached prompt input (not Anthropic cache_creation).
        "cache_miss": pick("prompt_cache_miss_tokens"),
        "cache_creation": pick("cache_creation_input_tokens"),
    }


def _text_from_content_blocks(content) -> str:
    """Return the first text block from a Messages `content` array.

    Flash / thinking models may put non-text blocks first; do not assume
    content[0] is a string text block.
    """
    if not isinstance(content, list) or not content:
        raise ValueError("missing content block in Messages response")
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text" and isinstance(block.get("text"), str):
            return block["text"]
        # Some gateways omit type but still send text.
        if "text" in block and isinstance(block.get("text"), str) and block.get("type") in (
            None,
            "text",
        ):
            return block["text"]
    raise ValueError(
        f"no text content block in Messages response "
        f"(block types={[b.get('type') if isinstance(b, dict) else type(b).__name__ for b in content]})"
    )


def _provider_prefs_from_env() -> dict | None:
    """Parse SITE_CRAWL_PROVIDER_JSON; return None if unset/empty."""
    raw = SITE_CRAWL_PROVIDER_JSON
    if not raw:
        return None
    prefs = json.loads(raw)
    if not isinstance(prefs, dict):
        raise ValueError("SITE_CRAWL_PROVIDER_JSON must be a JSON object")
    return prefs


def _serving_meta_from_response(result: dict, resp_headers) -> dict[str, str]:
    """Best-effort serving provider / quant / generation id from OR or DS."""
    provider = "unknown"
    quantization = "unknown"
    generation_id = "unknown"

    for key in ("provider", "provider_name", "served_by"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            provider = val.strip()
            break
        if isinstance(val, dict):
            name = val.get("name") or val.get("slug") or val.get("id")
            if isinstance(name, str) and name.strip():
                provider = name.strip()
            quant = val.get("quantization") or val.get("quant")
            if isinstance(quant, str) and quant.strip():
                quantization = quant.strip()
            break

    for key in ("quantization", "quant"):
        val = result.get(key)
        if isinstance(val, str) and val.strip():
            quantization = val.strip()
            break

    gen = result.get("id")
    if isinstance(gen, str) and gen.strip():
        generation_id = gen.strip()

    if resp_headers is not None:
        for hk, dest in (
            ("x-openrouter-provider", "provider"),
            ("x-provider", "provider"),
            ("x-openrouter-quantization", "quantization"),
        ):
            hv = resp_headers.get(hk)
            if hv and dest == "provider" and provider == "unknown":
                provider = hv.strip()
            elif hv and dest == "quantization" and quantization == "unknown":
                quantization = hv.strip()

    return {
        "provider": provider,
        "quantization": quantization,
        "generation_id": generation_id,
    }


def _log_site_crawl_usage(
    *,
    seed_id: str,
    url_count: int,
    status: str = "ok",
    error: str | None = None,
    unparsed_urls: int = 0,
    usage: dict[str, int] | None = None,
    serving: dict[str, str] | None = None,
) -> None:
    parts = [
        "SITE_CRAWL_USAGE",
        f"status={status}",
        f"model={SCREEN_MODEL}",
        f"seed={seed_id}",
        f"urls={url_count}",
    ]
    if serving:
        parts.extend(
            [
                f"provider={serving.get('provider', 'unknown')}",
                f"quantization={serving.get('quantization', 'unknown')}",
                f"generation_id={serving.get('generation_id', 'unknown')}",
            ]
        )
    if status == "ok" and usage is not None:
        parts.extend(
            [
                f"input_tokens={usage['input_tokens']}",
                f"output_tokens={usage['output_tokens']}",
                f"cache_read={usage['cache_read']}",
                f"cache_miss={usage['cache_miss']}",
                f"cache_creation={usage['cache_creation']}",
                f"unparsed_urls={unparsed_urls}",
            ]
        )
        _usage_run_totals["calls"] += 1
        _usage_run_totals["input_tokens"] += usage["input_tokens"]
        _usage_run_totals["output_tokens"] += usage["output_tokens"]
        _usage_run_totals["cache_read"] += usage["cache_read"]
        _usage_run_totals["cache_miss"] += usage["cache_miss"]
        _usage_run_totals["cache_creation"] += usage["cache_creation"]
        _usage_run_totals["unparsed_urls"] += unparsed_urls
    elif status == "error":
        _usage_run_totals["errors"] += 1
        err = json.dumps((error or "unknown")[:200])
        parts.append(f"error={err}")
    print(" ".join(parts))


def _log_site_crawl_usage_total() -> None:
    if _usage_run_totals["calls"] == 0 and _usage_run_totals["errors"] == 0:
        return
    print(
        "SITE_CRAWL_USAGE_TOTAL"
        f" calls={_usage_run_totals['calls']}"
        f" errors={_usage_run_totals['errors']}"
        f" input_tokens={_usage_run_totals['input_tokens']}"
        f" output_tokens={_usage_run_totals['output_tokens']}"
        f" cache_read={_usage_run_totals['cache_read']}"
        f" cache_miss={_usage_run_totals['cache_miss']}"
        f" cache_creation={_usage_run_totals['cache_creation']}"
        f" unparsed_urls={_usage_run_totals['unparsed_urls']}"
    )

def filter_urls_to_seed_prefix(urls: list[str], seed_url: str) -> list[str]:
    """Keep only URLs under the seed's path prefix; drop TOC/index stubs.

    Example (sre-workbook): seed
    ``https://sre.google/workbook/table-of-contents/`` → prefix
    ``https://sre.google/workbook``; keep chapter URLs, drop TOC/root.
    """
    prefix = get_site_prefix(seed_url).rstrip("/")
    seed_norm = seed_url.rstrip("/")
    filtered = []
    for raw in urls:
        u = raw.split("#")[0].rstrip("/")
        if not u.startswith(prefix):
            continue
        if u == seed_norm or u == prefix:
            continue
        lower = u.lower()
        if "/table-of-contents" in lower:
            continue
        # Bare section index pages (…/workbook or …/docs) already dropped via
        # prefix equality; also skip …/index and …/index.html
        path = urlparse(u).path.rstrip("/")
        if path.endswith("/index") or path.endswith("/index.html"):
            continue
        # Skip common non-content paths (shared with nav discovery)
        skip_patterns = (
            "/api/", "/assets/", "/static/", "/css/", "/js/",
            "/images/", "/fonts/", ".css", ".js", ".png", ".jpg",
            ".svg", ".ico", ".xml", ".json",
        )
        if any(p in lower for p in skip_patterns):
            continue
        filtered.append(u)
    return filtered


def load_seeds() -> dict:
    with open(SEEDS_PATH) as f:
        return json.load(f)


def load_state() -> dict:
    if STATE_PATH.exists():
        with open(STATE_PATH) as f:
            return json.load(f)
    return {}


def save_state(state: dict):
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_PATH, "w") as f:
        json.dump(state, f, indent=2, default=str)


def get_base_url(url: str) -> str:
    """Extract scheme + netloc from a URL for same-site filtering."""
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def get_site_prefix(url: str) -> str:
    """Get the URL path prefix for scoping crawls to the same site section.

    Walks up from the seed URL path to find a sensible project root.
    For https://example.com/gh-aw/introduction/overview/ → /gh-aw
    For https://example.com/docs/guide/ → /docs
    Uses the first two non-empty path segments as the root.
    """
    parsed = urlparse(url)
    segments = [s for s in parsed.path.split("/") if s]
    # Use the first path segment as the project root (e.g. "gh-aw")
    if segments:
        root = "/" + segments[0]
    else:
        root = "/"
    return f"{parsed.scheme}://{parsed.netloc}{root}"


def discover_from_sitemap(seed_url: str) -> list[str] | None:
    """Try to fetch and parse sitemap.xml. Returns URLs or None if no sitemap."""
    base = get_base_url(seed_url)
    sitemap_urls = [
        f"{base}/sitemap.xml",
        f"{base}/sitemap_index.xml",
    ]

    for sitemap_url in sitemap_urls:
        try:
            resp = requests.get(
                sitemap_url,
                headers={"User-Agent": USER_AGENT},
                timeout=REQUEST_TIMEOUT,
            )
            if resp.status_code != 200:
                continue

            # Parse sitemap XML
            import xml.etree.ElementTree as ET
            root = ET.fromstring(resp.text)

            # Handle sitemap index (contains <sitemap><loc>) or
            # urlset (contains <url><loc>)
            ns = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
            urls = []

            # Try urlset first
            for url_el in root.findall(".//sm:url/sm:loc", ns):
                if url_el.text:
                    urls.append(url_el.text.strip())

            # Try without namespace (some sitemaps don't use it)
            if not urls:
                for url_el in root.findall(".//url/loc"):
                    if url_el.text:
                        urls.append(url_el.text.strip())

            if urls:
                print(f"  Found sitemap at {sitemap_url} with {len(urls)} URLs")
                return urls

        except Exception as e:
            print(f"  Sitemap {sitemap_url}: {e}", file=sys.stderr)
            continue

    return None


def discover_from_nav(seed_url: str) -> list[str]:
    """Fetch the seed page and extract internal links."""
    try:
        resp = requests.get(
            seed_url,
            headers={"User-Agent": USER_AGENT},
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code != 200:
            print(f"  ERROR fetching seed {seed_url}: HTTP {resp.status_code}", file=sys.stderr)
            return []
    except requests.RequestException as e:
        print(f"  ERROR fetching seed {seed_url}: {e}", file=sys.stderr)
        return []

    # Extract all href links from the HTML
    hrefs = re.findall(r'href=["\']([^"\']+)["\']', resp.text)

    base = get_base_url(seed_url)
    prefix = get_site_prefix(seed_url)
    urls = set()

    for href in hrefs:
        # Resolve relative URLs
        full_url = urljoin(seed_url, href)
        # Strip fragments
        full_url = full_url.split("#")[0]
        # Strip trailing slash for consistency
        full_url = full_url.rstrip("/")

        # Only keep same-site URLs under the same path prefix
        if full_url.startswith(prefix) and full_url != seed_url.rstrip("/"):
            # Skip common non-content paths
            skip_patterns = [
                "/api/", "/assets/", "/static/", "/css/", "/js/",
                "/images/", "/fonts/", ".css", ".js", ".png", ".jpg",
                ".svg", ".ico", ".xml", ".json",
            ]
            if not any(p in full_url.lower() for p in skip_patterns):
                urls.add(full_url)

    print(f"  Extracted {len(urls)} internal links from seed page")
    return sorted(urls)


def screen_urls_with_flash(urls: list[str], seed: dict) -> dict[str, str]:
    """Batch-screen URLs for relevance using DeepSeek Flash.

    Returns {url: "relevant"|"rejected"} with a one-line reason for each.
    """
    if not ANTHROPIC_API_KEY:
        print(
            "  WARNING: DEEPSEEK_API_KEY/ANTHROPIC_API_KEY not set — "
            "marking all URLs as pending",
            file=sys.stderr,
        )
        return {url: "pending" for url in urls}

    # Build a compact list for the screener model
    url_list = "\n".join(f"- {url}" for url in urls)

    prompt = f"""You are a fast relevance screener for the SRE AI LLM Work guide.

Given these URLs from a documentation site, decide which pages are likely to contain
practitioner insights relevant to SRE work with AI/LLMs: incident response, on-call,
observability, runbooks/agents, toil reduction, LLM ops reliability, or AI-in-ops security.

Scope hint from the curator: {seed.get('scope', 'no specific scope')}

URLs to screen:
{url_list}

For each URL, respond with exactly one line in this format:
URL | RELEVANT | one-line reason
URL | REJECT | one-line reason

Base your decision on the URL path structure and page name — you cannot read the pages.
Reject API reference pages, changelog/release-note pages, installation/setup guides
that are purely mechanical, pure AI coding-agent lifestyle content with no ops angle,
and marketing/careers pages.
When in doubt, mark as RELEVANT — the Prospector will do the deep evaluation later."""

    serving: dict[str, str] | None = None
    try:
        body: dict = {
            "model": SCREEN_MODEL,
            "max_tokens": 4096,
            "messages": [{"role": "user", "content": prompt}],
        }
        provider_prefs = _provider_prefs_from_env()
        if provider_prefs is not None:
            body["provider"] = provider_prefs

        headers = {
            "x-api-key": ANTHROPIC_API_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        }
        if "openrouter.ai" in ANTHROPIC_BASE_URL:
            headers["Authorization"] = f"Bearer {ANTHROPIC_API_KEY}"
            headers["HTTP-Referer"] = f"https://github.com/{REPO_URL}"
            headers["X-Title"] = "sre-ai-llm-work-site-crawl"

        resp = requests.post(
            f"{ANTHROPIC_BASE_URL}/v1/messages",
            headers=headers,
            json=body,
            timeout=60,
        )
        resp.raise_for_status()
        result = resp.json()
        if not isinstance(result, dict):
            raise ValueError(f"unexpected response type: {type(result).__name__}")
        serving = _serving_meta_from_response(result, resp.headers)
        text = _text_from_content_blocks(result.get("content") or [])
    except Exception as e:
        print(f"  ERROR calling screener model for screening: {e}", file=sys.stderr)
        _log_site_crawl_usage(
            seed_id=seed.get("id", "unknown"),
            url_count=len(urls),
            status="error",
            error=str(e),
            serving=serving,
        )
        return {url: "pending" for url in urls}

    try:
        usage = _usage_from_response(result)

        # Parse the response
        verdicts = {}
        for line in text.strip().split("\n"):
            line = line.strip()
            if not line or "|" not in line:
                continue
            parts = [p.strip() for p in line.split("|", 2)]
            if len(parts) < 2:
                continue
            url = parts[0]
            verdict = parts[1].upper()
            # Match URL back to our list (model might slightly mangle URLs)
            matched_url = None
            for u in urls:
                if u in url or url in u:
                    matched_url = u
                    break
            if matched_url:
                if "RELEV" in verdict and "REJECT" not in verdict:
                    verdicts[matched_url] = "pending"
                elif "REJECT" in verdict:
                    verdicts[matched_url] = "rejected"
                # Other verdict labels stay out of verdicts → unparsed_urls

        # URLs with no matching model line → pending (filed like other pending)
        unparsed_urls = 0
        for url in urls:
            if url not in verdicts:
                verdicts[url] = "pending"
                unparsed_urls += 1

        _log_site_crawl_usage(
            seed_id=seed.get("id", "unknown"),
            url_count=len(urls),
            status="ok",
            unparsed_urls=unparsed_urls,
            usage=usage,
            serving=serving,
        )
    except Exception as e:
        print(f"  ERROR parsing screener response: {e}", file=sys.stderr)
        _log_site_crawl_usage(
            seed_id=seed.get("id", "unknown"),
            url_count=len(urls),
            status="error",
            error=str(e),
            serving=serving,
        )
        return {url: "pending" for url in urls}

    relevant = sum(1 for v in verdicts.values() if v == "pending")
    rejected = sum(1 for v in verdicts.values() if v == "rejected")
    print(f"  Flash screening: {relevant} relevant, {rejected} rejected")

    return verdicts


def file_issue(seed: dict, url: str) -> int | None:
    """File a source-submission issue for a discovered page. Returns issue number or None."""
    if shutil.which("gh") is None:
        print("  ERROR: `gh` CLI not found", file=sys.stderr)
        return None

    # Extract a readable title from the URL path
    parsed = urlparse(url)
    path_parts = [p for p in parsed.path.split("/") if p]
    title_slug = " ".join(path_parts[-2:]) if len(path_parts) >= 2 else path_parts[-1] if path_parts else "untitled"
    title = f"[source] {seed['id']}: {title_slug}"[:100]

    body = f"""### Source URL

{url}

### Source Type

{seed['source_type']}

### What's interesting about this source?

Auto-discovered from site-crawl seed `{seed['id']}`.

- **Seed URL**: {seed['url']}
- **Scope**: {seed.get('scope', 'none specified')}

This page was discovered via sitemap/nav-link crawling and passed a
DeepSeek Flash relevance screen. The Prospector still needs to evaluate novelty
and chapter relevance.

### Where might this be relevant?

Unknown — Prospector to determine.

### Key claims or patterns you noticed (optional)

(none — auto-filed, page has not been deep-read)

---
*Filed by `scripts/scan-sites.py` from site-crawl seed `{seed['id']}`*
"""

    cmd = [
        "gh", "issue", "create",
        "--repo", REPO_URL,
        "--title", title,
        "--body", body,
        "--label", "new-source",
        "--label", "source-submission",
    ]

    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        issue_url = result.stdout.strip()
        print(f"  Filed: {issue_url}")
        # Extract issue number from URL
        match = re.search(r"/issues/(\d+)", issue_url)
        return int(match.group(1)) if match else None
    except subprocess.CalledProcessError as e:
        print(f"  Failed to file issue for {url} (exit {e.returncode}): {e.stderr.strip()}", file=sys.stderr)
        return None


def scan_seed(
    seed: dict,
    state: dict,
    dry_run: bool = False,
    *,
    measure_only: bool = False,
    rescreen: bool = False,
) -> tuple[int, int, int]:
    """Scan one seed. Returns (new_urls_found, issues_filed, pending_count).

    dry_run: skip Flash + skip filing (legacy discovery-only).
    measure_only: run Flash, log usage; do not file or persist state updates
      (caller skips save_state). Used for #1113 Phase 0 A/B.
    rescreen: screen already-known URLs too (needed when state is warm).
    """
    seed_id = seed["id"]
    print(f"\nScanning seed: {seed_id} ({seed['url']})")

    seed_state = state.setdefault(seed_id, {"urls": {}, "last_scan": None})
    known_urls = seed_state["urls"]

    # Phase 1: Discover URLs, then always apply shared prefix/TOC/index filter
    # (nav discovery already path-prefixes; filter still drops TOC/index stubs).
    urls = discover_from_sitemap(seed["url"])
    source = "sitemap"
    if urls is None:
        print("  No sitemap found, falling back to nav-link extraction")
        urls = discover_from_nav(seed["url"]) or []
        source = "nav"
    else:
        before = len(urls)
        urls = filter_urls_to_seed_prefix(urls, seed["url"])
        print(
            f"  Prefix-filtered sitemap: {before} → {len(urls)} "
            f"(prefix={get_site_prefix(seed['url'])})"
        )
        # Some sites (e.g. sre.google) publish a site-wide sitemap that
        # omits the seed section entirely — fall back to nav crawl.
        if not urls:
            print("  Prefix filter emptied sitemap; falling back to nav-link extraction")
            urls = discover_from_nav(seed["url"]) or []
            source = "nav"

    if urls and source == "nav":
        before = len(urls)
        urls = filter_urls_to_seed_prefix(urls, seed["url"])
        print(
            f"  Prefix-filtered nav: {before} → {len(urls)} "
            f"(prefix={get_site_prefix(seed['url'])})"
        )

    if not urls:
        print("  No URLs discovered")
        return (0, 0, 0)

    # Filter to new URLs only (unless rescreen for measurement A/B)
    new_urls = [u for u in urls if u not in known_urls]
    print(f"  {len(new_urls)} new URLs (of {len(urls)} total)")

    if not new_urls and not rescreen:
        seed_state["last_scan"] = datetime.now(timezone.utc).isoformat()
        return (
            0,
            0,
            sum(
                1
                for v in known_urls.values()
                if isinstance(v, dict) and v.get("status") == "pending"
            ),
        )

    # Cap screening per seed (max_per_run), with global MAX_SCREEN_PER_SEED ceiling
    max_per_run = min(
        int(seed.get("max_per_run", DEFAULT_MAX_PER_RUN)),
        MAX_SCREEN_PER_SEED,
    )
    if rescreen:
        candidates = new_urls + [u for u in urls if u in known_urls]
        seen: set[str] = set()
        ordered: list[str] = []
        for u in candidates:
            if u not in seen:
                seen.add(u)
                ordered.append(u)
        to_screen = ordered[:max_per_run]
        print(f"  [rescreen] screening {len(to_screen)} URL(s) (cap={max_per_run})")
    else:
        to_screen = new_urls[:max_per_run]
        if len(new_urls) > max_per_run:
            print(
                f"  Capping screening at {max_per_run}/seed; "
                f"remaining {len(new_urls) - max_per_run} next run"
            )

    # Phase 2: Flash screening
    # dry_run skips Flash; measure_only still bills Flash (no file/persist).
    if dry_run and not measure_only:
        verdicts = {url: "pending" for url in to_screen}
        print("  [DRY-RUN] skipping Flash screening, marking all as pending")
    else:
        verdicts = screen_urls_with_flash(to_screen, seed)

    if measure_only:
        # Do not mutate crawl state during A/B measurement.
        pending = sum(
            1
            for v in known_urls.values()
            if isinstance(v, dict) and v.get("status") == "pending"
        )
        return (len(new_urls), 0, pending)

    # Update state with screening results
    for url, verdict in verdicts.items():
        known_urls[url] = {
            "status": verdict,
            "screened_at": datetime.now(timezone.utc).isoformat(),
        }

    seed_state["last_scan"] = datetime.now(timezone.utc).isoformat()

    new_found = len(new_urls)
    pending = sum(
        1
        for v in known_urls.values()
        if isinstance(v, dict) and v.get("status") == "pending"
    )
    return (new_found, 0, pending)


def file_pending(state: dict, seeds_by_id: dict, dry_run: bool = False) -> int:
    """File issues for pending URLs across all seeds. Returns count filed."""
    filed = 0

    for seed_id, seed_state in state.items():
        if seed_id not in seeds_by_id:
            continue
        seed = seeds_by_id[seed_id]
        max_per_run = int(seed.get("max_per_run", DEFAULT_MAX_PER_RUN))
        filed_this_seed = 0

        for url, info in list(seed_state.get("urls", {}).items()):
            if not isinstance(info, dict) or info.get("status") != "pending":
                continue
            if filed >= MAX_ISSUES_PER_RUN:
                print(f"\n  Hit per-run cap of {MAX_ISSUES_PER_RUN} issues. Remaining pending URLs will be filed next run.")
                return filed
            if filed_this_seed >= max_per_run:
                print(
                    f"  [{seed_id}] Hit per-seed max_per_run={max_per_run}; "
                    f"remaining pending URLs next run"
                )
                break
            if scan_budget.remaining() <= 0:
                print(f"\n  Daily budget exhausted. Remaining pending URLs will be filed next run.")
                return filed

            if not dry_run and scan_dedup.is_url_already_tracked(url):
                print(f"  [dedup] already tracked: {url}")
                info["status"] = "deduped"
                continue

            if dry_run:
                print(f"  [DRY-RUN] would file: {url}")
                filed += 1
                filed_this_seed += 1
            else:
                issue_num = file_issue(seed, url)
                if issue_num is not None:
                    info["status"] = "filed"
                    info["issue"] = issue_num
                    info["filed_at"] = datetime.now(timezone.utc).isoformat()
                    filed += 1
                    filed_this_seed += 1
                    scan_budget.record_filed(1)
                else:
                    # Don't retry failed filings forever
                    info["status"] = "file_failed"

            time.sleep(INTER_REQUEST_SLEEP)

    return filed


def main():
    parser = argparse.ArgumentParser(description="Scan documentation site seeds for new relevant pages.")
    parser.add_argument("--dry-run", action="store_true", help="Discover only; skip Flash and filing.")
    parser.add_argument(
        "--measure-only",
        action="store_true",
        help="Run Flash screening and usage logs; skip filing and state writes (A/B).",
    )
    parser.add_argument(
        "--rescreen",
        action="store_true",
        help="Re-screen known URLs (for billed A/B when state is warm).",
    )
    parser.add_argument("--seed", help="Only scan the seed with this id.")
    parser.add_argument(
        "--max-seeds",
        type=int,
        default=0,
        help="Limit number of seeds processed (0 = all). Useful for A/B cost control.",
    )
    args = parser.parse_args()

    _reset_usage_run_totals()

    seeds_data = load_seeds()
    state = load_state()

    seeds = seeds_data.get("seeds", [])
    if args.seed:
        seeds = [s for s in seeds if s["id"] == args.seed]
        if not seeds:
            print(f"ERROR: no seed with id={args.seed} in {SEEDS_PATH}", file=sys.stderr)
            sys.exit(1)
    if args.max_seeds and args.max_seeds > 0:
        seeds = seeds[: args.max_seeds]

    seeds_by_id = {s["id"]: s for s in seeds_data.get("seeds", [])}

    print(
        f"scan-sites starting: {len(seeds)} seed(s), {scan_budget.status_summary()}"
        f", model={SCREEN_MODEL}, base={ANTHROPIC_BASE_URL}"
        f", provider_json={'set' if SITE_CRAWL_PROVIDER_JSON else 'unset'}"
        f", measure_only={args.measure_only}, rescreen={args.rescreen}"
    )

    # Phase 1+2: Discover and screen new URLs
    total_new = 0
    total_pending = 0
    for i, seed in enumerate(seeds):
        try:
            new, _, pending = scan_seed(
                seed,
                state,
                dry_run=args.dry_run,
                measure_only=args.measure_only,
                rescreen=args.rescreen,
            )
            total_new += new
            total_pending += pending
        except Exception as e:
            print(f"  ERROR scanning seed {seed.get('id', '?')}: {e}", file=sys.stderr)
        if i < len(seeds) - 1:
            time.sleep(INTER_REQUEST_SLEEP)

    # Phase 3: File issues from pending queue (skipped for measure-only A/B)
    if args.measure_only:
        print("\n[measure-only] skipping issue filing and state save")
        filed = 0
    else:
        print(f"\nFiling issues from pending queue ({total_pending} pending)...")
        filed = file_pending(state, seeds_by_id, dry_run=args.dry_run)
        if not args.dry_run:
            save_state(state)

    print(
        f"\nScan complete: {total_new} new URLs discovered, {filed} issue(s) filed, "
        f"{total_pending - filed} still pending"
    )
    print(f"Final budget: {scan_budget.status_summary()}")
    _log_site_crawl_usage_total()


if __name__ == "__main__":
    main()
