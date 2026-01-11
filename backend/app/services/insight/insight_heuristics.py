from __future__ import annotations

from typing import List, Dict
import re


DEFAULT_GAP_PATTERNS = [
    r"\bnot evaluated\b",
    r"\blimited to\b",
    r"\bfuture work\b",
    r"\bnot explored\b",
    r"\black of\b",
    r"\bremains unclear\b",
    r"\bnot studied\b",
    r"\bwe leave\b.*\bfuture\b",
]


def detect_gaps(
    texts: List[str],
    patterns: List[str] | None = None,
    max_hits: int = 12,
) -> List[str]:

    pats = patterns or DEFAULT_GAP_PATTERNS
    joined = " ".join([t for t in texts if t]).lower()

    hits: List[str] = []
    for pat in pats:
        if re.search(pat, joined):
            hits.append(f"heuristic_signal:{pat}")

    return hits[:max_hits]
