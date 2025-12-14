from typing import List
from rapidfuzz import fuzz


def faithfulness_score(answer: str, passages: List[str]) -> float:
    if not answer or not passages:
        return 0.0

    scores = []
    for p in passages:
        scores.append(fuzz.partial_ratio(answer, p) / 100)

    return min(1.0, sum(scores) / len(scores))
