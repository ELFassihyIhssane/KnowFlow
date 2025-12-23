from __future__ import annotations

import re
from typing import List, Optional
from rapidfuzz import fuzz


# --- 1) Normalisation ID (machine-friendly) ---
def normalize_label(label: str) -> str:
    """
    Normalise pour un ID stable, en préservant les patterns scientifiques:
    - versions: 4.1, v2.0
    - modèles: flux.1, gpt-4.1
    - ratios: p@1, f1 (ici on conserve chiffres/lettres)
    - chemins: vit-b/16
    """
    s = (label or "").strip().lower()
    s = re.sub(r"\s+", " ", s)

    # Fix PDF hyphenation: "rein- forcement" -> "reinforcement"
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)

    # Allow: letters, digits, space, '-', '_', '/', '.' and '+'
    s = re.sub(r"[^a-z0-9\-\s_/\.\\+]", "", s)
    s = s.strip()

    # Collapse spaces to single dash for IDs if you want more compact IDs
    # (optional - if you prefer keep spaces, comment this)
    s = s.replace(" ", "-")

    # Avoid empty ids
    return s or "concept"


# --- 2) Canonicalisation label (human-friendly & generic) ---
def canonicalize_concept(label: str) -> str:
    """
    Nettoie un label sans être dépendant d'un domaine spécifique.
    Important: ne pas inventer -> seulement nettoyer.
    """
    s = (label or "").strip()
    if not s:
        return ""

    # Normalize spaces
    s = re.sub(r"\s+", " ", s).strip()

    # Fix PDF hyphenation
    s = re.sub(r"(\w)-\s+(\w)", r"\1\2", s)

    # Remove surrounding quotes / bullets
    s = s.strip("•-*\"'“”‘’")

    # Lowercase only for comparison, but keep original casing style lightly
    low = s.lower()

    # Remove weak trailing words (generic, not domain-specific)
    low = re.sub(r"\b(training|method|approach|framework|model)\b$", "", low).strip()

    # Remove weak adjectives that inflate duplicates
    weak_words = {"many", "diverse", "various", "external", "novel", "new"}
    tokens = [t for t in low.split() if t and t not in weak_words]

    out = " ".join(tokens).strip()

    # Restore nicer casing: keep original if it contains CamelCase/acronyms
    # Otherwise return lowercase phrase (consistent KG)
    if re.search(r"[A-Z]", s):  # contains uppercase → keep original cleaned
        return s if len(s) <= 70 else s[:70].strip()
    return out if len(out) <= 70 else out[:70].strip()


# --- 3) Choose best canonical label for merged nodes ---
def choose_canonical(existing: str, incoming: str) -> str:
    """
    Choisit un label lisible et stable.
    Préfère 2-6 mots, évite tokens meta.
    """
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

        # too short or too long
        if len(words) < 1:
            p += 2.0
        if len(words) > 8:
            p += (len(words) - 8) * 0.8

        # bonus for "name-like" scientific patterns
        bonus = 0.0
        if 2 <= len(words) <= 6:
            bonus += 2.0
        if re.search(r"[a-z][A-Z]", s):  # CamelCase
            bonus += 1.2
        if re.fullmatch(r"[A-Z]{2,6}s?", s.strip()):
            bonus += 1.0
        if re.search(r"\b(v\d+|\d+\.\d+|\d+B)\b", s, flags=re.IGNORECASE):
            bonus += 0.8

        return bonus - p

    return incoming if score(incoming) > score(existing) else existing


# --- 4) Fuzzy matching (more conservative) ---
def find_best_match(label: str, candidates: List[str], threshold: int = 90) -> Optional[str]:
    """
    Retourne le candidat le plus proche si similarité >= threshold.
    Utilise token_set_ratio (plus robuste).
    """
    if not label or len(label) < 4:
        return None

    best = None
    best_score = 0.0

    for c in candidates:
        if not c:
            continue
        # token_set_ratio is less fragile than ratio
        score = fuzz.token_set_ratio(label, c)
        # penalize if candidate is extremely short
        if len(c) <= 3:
            score -= 10

        if score > best_score:
            best_score = score
            best = c

    return best if best and best_score >= threshold else None
