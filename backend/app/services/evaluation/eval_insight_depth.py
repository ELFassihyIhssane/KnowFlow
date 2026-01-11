from __future__ import annotations

import re

KEY_TERMS = [
    "limitation", "limitations", "however", "gap", "challenge",
    "future", "trade-off", "contrast", "weakness", "risk", "assumption",
    "underexplored", "unclear", "open question", "bottleneck"
]


def insight_depth_score(answer: str) -> float:

    if not answer or not answer.strip():
        return 0.0

    low = answer.lower()
    hits = []
    for k in KEY_TERMS:
        if k in low:
            hits.append(k)

    unique_hits = len(set(hits))

    if unique_hits == 0:
        return 0.2 if len(answer.split()) >= 80 else 0.0

    return min(1.0, unique_hits / 6.0)
