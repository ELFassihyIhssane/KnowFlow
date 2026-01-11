from __future__ import annotations

from typing import List
import re
from rapidfuzz import fuzz


def _sentencize(text: str) -> List[str]:

    if not text:
        return []

    parts = re.split(r"[.!?]\s+|\n+", text.strip())
    sents = []
    for p in parts:
        p = p.strip()
        if len(p.split()) >= 8:  
            sents.append(p)
    return sents


def faithfulness_score(answer: str, passages: List[str]) -> float:

    if not answer or not passages:
        return 0.0

    sents = _sentencize(answer)
    if not sents:
        return 0.0

    best_scores = []
    for s in sents:
        best = 0.0
        for p in passages:
            if not p:
                continue
            score = max(
                fuzz.partial_ratio(s, p),
                fuzz.token_set_ratio(s, p),
            ) / 100.0
            if score > best:
                best = score
        best_scores.append(best)

    return min(1.0, sum(best_scores) / len(best_scores))
