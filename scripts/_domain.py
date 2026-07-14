"""
Domain relevance helpers for the SRE / LLM-ops pivot.

Reads `domain.exclude_pure_coding_agents` from hitchhiker.config.json and
classifies free text as SRE/LLM-ops relevant vs pure AI coding-agent DX.
"""

from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).parent.parent / "hitchhiker.config.json"

# Signals that the text is about production SRE / LLM-ops practice.
# Short tokens use word-boundary matching to avoid "sla"⊂"slash", "rag"⊂"drag".
SRE_OPS_PHRASES = (
    "runbook",
    "oncall",
    "on-call",
    "incident",
    "observability",
    "pagerduty",
    "postmortem",
    "post-mortem",
    "inference",
    "evals",
    "eval gate",
    "tracing",
    "opentelemetry",
    "toil",
    "reliability",
    "production",
    "platform eng",
    "llmops",
    "llm-ops",
    "mlops",
)

SRE_OPS_TOKENS = (
    "slo",
    "sli",
    "sla",
    "pager",
    "llm",
    "rag",
    "otel",
    "sre",
)

# Signals that the text is about coding-agent developer experience only.
CODING_AGENT_DX_PHRASES = (
    "claude code",
    "cursor rules",
    ".cursorrules",
    "copilot coding",
    "github copilot",
    "autodev",
    "coding agent",
    "ai coding",
    "vibe coding",
    "slash command",
    "claude.md",
    "agents.md tutorial",
    "prompt engineering for coding",
    "ide agent",
    "pair programming with ai",
    "show hn: i built a new ai coding",
)


@lru_cache(maxsize=1)
def _load_domain_config() -> dict:
    # Cached for the process lifetime — mid-run edits to hitchhiker.config.json
    # (or tests that flip domain flags) will not be picked up without a restart
    # or cache_clear(). Scanners load config once at start; that is intentional.
    if not CONFIG_PATH.exists():
        return {"exclude_pure_coding_agents": False}
    with open(CONFIG_PATH) as f:
        data = json.load(f)
    return data.get("domain", {})


def exclude_pure_coding_agents() -> bool:
    """True when hitchhiker.config.json asks scanners/pre-screen to filter DX noise."""
    return bool(_load_domain_config().get("exclude_pure_coding_agents", False))


def _contains_phrase(text: str, phrases: tuple[str, ...]) -> bool:
    return any(p in text for p in phrases)


def _contains_token(text: str, tokens: tuple[str, ...]) -> bool:
    for tok in tokens:
        if re.search(rf"\b{re.escape(tok)}\b", text):
            return True
    return False


def _has_sre_signal(text: str) -> bool:
    return _contains_phrase(text, SRE_OPS_PHRASES) or _contains_token(text, SRE_OPS_TOKENS)


def _has_coding_dx_signal(text: str) -> bool:
    return _contains_phrase(text, CODING_AGENT_DX_PHRASES)


def is_sre_relevant(text: str) -> bool:
    """True if text is about SRE/LLM ops; False if purely AI coding-agent DX.

    When `domain.exclude_pure_coding_agents` is false, always returns True.
    Ambiguous text (no strong DX signal, or DX + SRE signals together) passes.
    """
    if not exclude_pure_coding_agents():
        return True

    lowered = (text or "").lower()
    has_sre = _has_sre_signal(lowered)
    has_dx = _has_coding_dx_signal(lowered)

    if has_dx and not has_sre:
        return False
    return True


def domain_relevance(text: str) -> str:
    """Return `sre-ops` or `coding-agent` for issue-body / Prospector frontmatter."""
    return "sre-ops" if is_sre_relevant(text) else "coding-agent"
