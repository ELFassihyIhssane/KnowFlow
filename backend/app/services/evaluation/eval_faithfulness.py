from __future__ import annotations

from typing import List
import re
from rapidfuzz import fuzz


def _sentencize(text: str) -> List[str]:
    # Simple sentence splitter (robust enough for MVP)
    if not text:
        return []
    # split on ., !, ? and newlines
    parts = re.split(r"[.!?]\s+|\n+", text.strip())
    sents = []
    for p in parts:
        p = p.strip()
        if len(p.split()) >= 8:  # ignore tiny fragments
            sents.append(p)
    return sents


def faithfulness_score(answer: str, passages: List[str]) -> float:
    """
    Robust faithfulness proxy:
    - Split answer into sentences
    - For each sentence, find best-matching passage
    - Return mean(best_match_scores)

    This is much less punishing for paraphrases and long answers,
    and more aligned with "each claim should be supported by at least one passage".
    """
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
            # partial_ratio works well for paraphrase-ish overlaps; token_set_ratio adds robustness
            score = max(
                fuzz.partial_ratio(s, p),
                fuzz.token_set_ratio(s, p),
            ) / 100.0
            if score > best:
                best = score
        best_scores.append(best)

    # Average support across sentences
    return min(1.0, sum(best_scores) / len(best_scores))
