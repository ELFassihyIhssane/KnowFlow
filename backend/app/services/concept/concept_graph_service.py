from __future__ import annotations

import re
from typing import List, Optional
from rapidfuzz import fuzz


def normalize_label(label: str) -> str:
    s = (label or "").strip().lower()
    s = re.sub(r"\s+", " ", s)

    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)

    s = re.sub(r"[^a-z0-9\-\s_/\.\\+]", "", s)
    s = s.strip()

    s = s.replace(" ", "-")

    return s or "concept"

def canonicalize_concept(label: str) -> str:

    s = (label or "").strip()
    if not s:
        return ""

    s = re.sub(r"\s+", " ", s).strip()

    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)

    s = s.strip("•-*\"'“”‘’")

    low = s.lower()

    low = re.sub(r"\b(training|method|approach|framework|model)\b$", "", low).strip()

    weak_words = {"many", "diverse", "various", "external", "novel", "new"}
    tokens = [t for t in low.split() if t and t not in weak_words]

    out = " ".join(tokens).strip()

    if re.search(r"[A-Z]", s): 
        return s if len(s) <= 70 else s[:70].strip()
    return out if len(out) <= 70 else out[:70].strip()

def choose_canonical(existing: str, incoming: str) -> str:

    bad_starts = {"this", "our", "we", "these", "those", "the"}
    bad_tokens = {"paper", "results", "result", "work", "study", "section", "table", "figure"}

    def score(s: str) -> float:
        s = (s or "").strip()
        if not s:
            return -10.0

        low = s.lower()
        words = [w for w in re.split(r"\s+", low) if w]

        p = 0.0
        if words and words[0] in bad_starts:
            p += 2.5
        if any(t in bad_tokens for t in words):
            p += 2.0

        if len(words) < 1:
            p += 2.0
        if len(words) > 8:
            p += (len(words) - 8) * 0.8

        bonus = 0.0
        if 2 <= len(words) <= 6:
            bonus += 2.0
        if re.search(r"[a-z][A-Z]", s): 
            bonus += 1.2
        if re.fullmatch(r"[A-Z]{2,6}s?", s.strip()):
            bonus += 1.0
        if re.search(r"\b(v\d+|\d+\.\d+|\d+B)\b", s, flags=re.IGNORECASE):
            bonus += 0.8

        return bonus - p

    return incoming if score(incoming) > score(existing) else existing

def find_best_match(label: str, candidates: List[str], threshold: int = 90) -> Optional[str]:

    if not label or len(label) < 4:
        return None

    best = None
    best_score = 0.0

    for c in candidates:
        if not c:
            continue
        score = fuzz.token_set_ratio(label, c)

        if len(c) <= 3:
            score -= 10

        if score > best_score:
            best_score = score
            best = c

    return best if best and best_score >= threshold else None
