from __future__ import annotations

import re
from typing import List, Set, Tuple

import spacy

_nlp = None


def get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def _tokenize(s: str) -> Set[str]:
    s = (s or "").lower()
    s = re.sub(r"[^a-z0-9\.\-\s_/]", " ", s)
    toks = {t for t in s.split() if len(t) > 2}
    return toks


def _shape_bonus(s: str) -> float:

    bonus = 0.0

    if re.search(r"[a-z][A-Z]", s):
        bonus += 1.5

    if re.fullmatch(r"[A-Z]{2,6}s?", s.strip()):
        bonus += 1.5

    if re.search(r"\b(v\d+|\d+\.\d+|\d+B)\b", s, flags=re.IGNORECASE):
        bonus += 1.2

    if "-" in s and len(s) <= 40:
        bonus += 0.6

    if re.search(r"\b(ms|s|sec|gb|mb|tf|gflops|fid|bleu|auc|f1)\b", s, flags=re.IGNORECASE):
        bonus += 1.0

    return bonus


def extract_concepts(text: str, question: str = "", max_concepts: int = 30) -> List[str]:
    if not text:
        return []

    nlp = get_nlp()
    doc = nlp(text)

    stop_starts = {"the", "a", "an", "this", "our", "we", "these", "those"}
    narrative_tokens = {"show", "shows", "demonstrate", "demonstrates", "prove", "proves", "suggest", "suggests"}
    meta_tokens = {"paper", "work", "study", "section", "table", "figure", "result", "results", "approach", "method"}

    blacklist_tokens = {
        "foundation", "grant", "funded", "support",
        "algorithm", "figure", "table", "appendix",
        "university", "institute", "laboratory",
        "acknowledgement", "acknowledgment",
    }

    q_toks = _tokenize(question)
    q_has_signal = len(q_toks) > 0

    def clean_phrase(s: str) -> str:
        return " ".join((s or "").strip().split())

    def looks_like_reference(s: str) -> bool:
        low = s.lower()
        if re.search(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]", s):
            return True
        if re.search(r"\b(algorithm|figure|table)\s+\d+\b", low):
            return True
        if "et al" in low:
            return True
        return False

    def looks_like_person_name(s: str) -> bool:
        tokens = [t for t in s.split() if t]
        if len(tokens) < 2:
            return False
        caps = sum(1 for w in tokens if w[0].isupper())
        return caps >= 2 and len(tokens) <= 4

    def is_good_concept(s: str) -> bool:
        if not s:
            return False
        if re.fullmatch(r"\d+(\.\d+)+", s.strip()):
            return False

        s = clean_phrase(s)
        low = s.lower()

        if looks_like_reference(s):
            return False
        if looks_like_person_name(s):
            return False
        if any(tok in low for tok in blacklist_tokens):
            return False

        if len(s) < 3 or len(s) > 70:
            return False

        words = [w for w in low.split() if w]
        if len(words) < 1 or len(words) > 8:
            return False

        if words and words[0] in stop_starts:
            return False
        if any(w in narrative_tokens for w in words):
            return False
        if sum(1 for w in words if w in meta_tokens) >= 2:
            return False
        if any(ch in s for ch in [";", ":", "\n"]):
            return False

        return True

    pool: List[Tuple[str, str]] = []  
    for ent in doc.ents:
        s = clean_phrase(ent.text)
        if is_good_concept(s):
            pool.append((s, "ent"))

    for chunk in doc.noun_chunks:
        s = clean_phrase(chunk.text)
        if is_good_concept(s):
            pool.append((s, "chunk"))

    seen = set()
    deduped: List[Tuple[str, str]] = []
    for s, src in pool:
        k = s.lower()
        if k in seen:
            continue
        seen.add(k)
        deduped.append((s, src))

    def score_concept(s: str, src: str) -> float:
        toks = _tokenize(s)
        overlap = len(toks & q_toks) if q_has_signal else 0

        ent_bonus = 1.0 if src == "ent" else 0.0

        shape = _shape_bonus(s)

        generic_penalty = 0.0
        if len(toks) == 1 and overlap == 0 and shape < 1.0:
            generic_penalty = 0.8

        length_penalty = 0.12 * max(0, len(s.split()) - 5)

        return (2.0 * overlap) + ent_bonus + shape - generic_penalty - length_penalty

    ranked = sorted(deduped, key=lambda x: score_concept(x[0], x[1]), reverse=True)

    if q_has_signal:
        kept = []
        for s, src in ranked:
            sc = score_concept(s, src)
            if sc >= 1.2 or _shape_bonus(s) >= 1.5:
                kept.append(s)
        ranked_out = kept
    else:
        ranked_out = [s for s, _ in ranked]

    return ranked_out[:max_concepts]

def looks_like_doi(s: str) -> bool:
    return bool(re.search(r"\b10\.\d{4,9}/\S+\b", s))

def looks_like_arxiv(s: str) -> bool:
    return bool(re.search(r"\barxiv:\s*\d{4}\.\d{4,5}\b", s.lower()))

def looks_like_venue(s: str) -> bool:
    low = s.lower()
    venues = ["neurips", "naacl", "icra", "icml", "cvpr", "eccv", "acl", "emnlp", "kdd", "ijcai"]
    return any(v in low for v in venues) or "conference on" in low or "proceedings" in low or "journal of" in low
