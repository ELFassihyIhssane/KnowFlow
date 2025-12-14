from __future__ import annotations

from typing import List
import spacy

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def extract_concepts(text: str, max_concepts: int = 30) -> List[str]:
    """
    Extraction simple:
    - entités nommées (ORG, PRODUCT, etc.)
    - noun chunks (groupes nominaux)
    """
    if not text:
        return []

    nlp = get_nlp()
    doc = nlp(text)

    concepts = set()

    # entities
    for ent in doc.ents:
        s = ent.text.strip()
        if 3 <= len(s) <= 60:
            concepts.add(s)

    # noun chunks
    for chunk in doc.noun_chunks:
        s = chunk.text.strip()
        if 3 <= len(s) <= 60:
            concepts.add(s)

    # limiter
    out = list(concepts)
    out.sort(key=lambda x: (-len(x), x))
    return out[:max_concepts]
