from __future__ import annotations

from typing import List, Optional
from rapidfuzz import fuzz


def _match_score(a: str, b: str) -> float:
    if not a or not b:
        return 0.0

    return fuzz.token_set_ratio(a, b) / 100.0


def coverage_score(question: str, answer: str, sub_tasks: Optional[List[str]] = None) -> float:

    if not question or not answer:
        return 0.0

    q_score = _match_score(question, answer)

    tasks = [t for t in (sub_tasks or []) if isinstance(t, str) and t.strip()]
    if not tasks:
        return min(1.0, q_score)

    task_scores = [_match_score(t, answer) for t in tasks]

    combined = 0.35 * q_score + 0.65 * (sum(task_scores) / len(task_scores))
    return min(1.0, combined)
