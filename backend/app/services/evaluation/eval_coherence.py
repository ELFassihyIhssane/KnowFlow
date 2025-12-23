from __future__ import annotations

import re


def coherence_score(answer: str) -> float:
    """
    Lightweight coherence proxy:
    - penalizes extremely short answers
    - rewards presence of multiple coherent sentences and connective markers
    Not perfect, but more meaningful than "sentence count only".
    """
    if not answer or not answer.strip():
        return 0.0

    words = answer.split()
    if len(words) < 40:
        return 0.35
    if len(words) < 90:
        base = 0.55
    else:
        base = 0.7

    # Count sentences (roughly)
    sentences = [s.strip() for s in re.split(r"[.!?]\s+|\n+", answer.strip()) if len(s.strip()) > 20]
    n_sent = len(sentences)

    # Connectives signal structure
    low = answer.lower()
    connectives = ["however", "therefore", "because", "in contrast", "whereas", "moreover", "thus", "overall"]
    conn_hits = sum(1 for c in connectives if c in low)

    # small bonuses
    bonus = 0.0
    if n_sent >= 3:
        bonus += 0.15
    if conn_hits >= 2:
        bonus += 0.1
    if conn_hits >= 4:
        bonus += 0.05

    return min(1.0, base + bonus)
