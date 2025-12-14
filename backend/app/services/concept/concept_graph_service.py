from __future__ import annotations

import re
from typing import Dict, List, Tuple

from rapidfuzz import fuzz


def normalize_label(label: str) -> str:
    s = (label or "").strip().lower()
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"[^a-z0-9\-\s_/]", "", s)
    return s.strip()


def choose_canonical(existing: str, incoming: str) -> str:
    # garde la version la plus "riche" (plus longue) comme label canonique
    return incoming if len(incoming) > len(existing) else existing


def find_best_match(label: str, candidates: List[str], threshold: int = 90) -> str | None:
    """
    Retourne l'id candidat le plus proche si similarité >= threshold.
    """
    best = None
    best_score = 0
    for c in candidates:
        score = fuzz.ratio(label, c)
        if score > best_score:
            best_score = score
            best = c
    return best if best and best_score >= threshold else None
