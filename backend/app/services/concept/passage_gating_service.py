from __future__ import annotations

import re
from typing import List, Tuple, Set


_PUNCT_RE = re.compile(r"[^a-z0-9\.\-\s_/]+", re.IGNORECASE)

_SECTION_PREFIX_RE = re.compile(r"^\s*\d+(?:\.\d+){1,4}\s*", re.IGNORECASE)
_CIT_RE = re.compile(r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]")

# tokens that are usually instructions, not topic
_STOP_INSTRUCTION = {
    "extract", "please", "pleaze", "concept", "concepts", "relation", "relations",
    "knowledge", "graph", "meaningful", "clear", "idea", "put", "make", "give",
    "generate", "build", "need", "want", "related", "topic", "about",
}

# ✅ Domain-agnostic "technique / eval" terms that often signal rich passages
_TECHNIQUE_HINTS = {
    "zero-shot", "few-shot", "one-shot",
    "chain-of-thought", "cot",
    "persona", "explanatory", "explanation",
    "prompt", "prompting", "prompt-engineering", "prompt engineering",
    "codebook", "automatic", "ape", "auto",
    "strategy", "strategies",
    "evaluation", "evaluated", "metric", "metrics",
    "accuracy", "precision", "recall", "f1", "confidence", "interval",
}

def _clean_passage(p: str) -> str:
    p = (p or "").strip()
    if not p:
        return ""

    p = _CIT_RE.sub("", p)
    p = _SECTION_PREFIX_RE.sub("", p)

    # Fix common PDF hyphenation splits: "post- training" -> "post-training"
    p = re.sub(r"(\w)-\s+(\w)", r"\1-\2", p)

    p = re.sub(r"\s+", " ", p).strip()
    return p


def _tokenize(s: str) -> Set[str]:
    s = (s or "").lower()
    s = _PUNCT_RE.sub(" ", s)
    toks = {t for t in s.split() if len(t) > 2}
    return {t for t in toks if t not in _STOP_INSTRUCTION}


def _expand_question(question: str) -> str:
    """
    Expand short queries so overlap-gating works even when passages use long forms.
    This is not hallucination: only synonym hints to improve gating.
    """
    q = (question or "").strip()
    low = q.lower()

    expansions: List[str] = []

    # PEFT family
    if "lora" in low:
        expansions += [
            "low rank adaptation",
            "low-rank adaptation",
            "parameter efficient fine tuning",
            "peft",
            "adapter",
            "rank",
        ]

    if "gpt" in low:
        expansions += ["llm", "large language model", "transformer"]

    # Argos/MMRL reward verifier
    if "argos" in low or "mmrl" in low:
        expansions += [
            "agentic verifier",
            "aggregated reward",
            "reward components",
            "scoring functions",
            "teacher models",
            "multi objective reward",
            "noisy reward signals",
        ]

    # TBA (Trajectory Balance with Asynchrony)
    if "tba" in low or ("trajectory" in low and "balance" in low):
        expansions += [
            "trajectory balance with asynchrony",
            "trajectory balance",
            "asynchrony",
            "asynchronous",
            "off policy",
            "off-policy",
            "experience replay buffer",
            "experience replay buffers",
            "replay buffer",
            "vargrad",
            "value network",
            "partition function",
            "z(x)",
            "control variate",
            "posterior",
            "gflownets",
            "gflow nets",
        ]

    # Prompt-engineering family (helps your prompt-technique case)
    if "prompt" in low or "prompting" in low:
        expansions += [
            "zero-shot",
            "few-shot",
            "persona prompting",
            "chain-of-thought",
            "explanatory prompting",
            "automatic prompt engineering",
            "codebook guided",
            "evaluation metrics",
        ]

    if not expansions:
        return q

    return q + " " + " ".join(expansions)


def _score_overlap(question: str, passage: str) -> float:
    q = _tokenize(question)
    p = _tokenize(passage)
    if not q or not p:
        return 0.0
    return float(len(q & p))


def _technique_bonus(passage: str) -> float:
    """
    Small bonus to passages that look "technique dense".
    Prevents losing passages listing actual strategies (persona, few-shot, etc.)
    when the question is generic.
    """
    toks = _tokenize(passage)
    if not toks:
        return 0.0
    hits = 0
    for t in _TECHNIQUE_HINTS:
        # allow multiword hints
        if " " in t:
            if t in (passage or "").lower():
                hits += 1
        else:
            if t in toks:
                hits += 1
    # soft cap
    return min(3.0, 0.35 * float(hits))


def _jaccard(a: Set[str], b: Set[str]) -> float:
    if not a or not b:
        return 0.0
    inter = len(a & b)
    uni = len(a | b)
    return inter / max(1, uni)


def _select_diverse_mmr(
    scored: List[Tuple[str, float]],
    top_k: int,
    lambda_div: float = 0.65,
) -> List[Tuple[str, float]]:
    """
    MMR-like selection:
    - pick highest score first
    - then pick next maximizing: lambda*score - (1-lambda)*similarity_to_selected
    Similarity computed as Jaccard over token sets.
    """
    if not scored:
        return []
    if top_k <= 1:
        return scored[:1]

    # Precompute token sets for passages
    tok_cache = {p: _tokenize(p) for p, _ in scored}

    selected: List[Tuple[str, float]] = []
    remaining = scored[:]

    # start with best
    selected.append(remaining.pop(0))

    while remaining and len(selected) < top_k:
        best_idx = 0
        best_mmr = -1e9

        selected_ps = [p for p, _ in selected]

        for i, (p, base) in enumerate(remaining):
            sim = 0.0
            p_toks = tok_cache.get(p, set())
            for sp in selected_ps:
                sim = max(sim, _jaccard(p_toks, tok_cache.get(sp, set())))
            mmr = lambda_div * base - (1.0 - lambda_div) * sim
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = i

        selected.append(remaining.pop(best_idx))

    return selected


def gate_passages(
    question: str,
    passages: List[str],
    top_k: int = 10,          # ✅ higher default for KG recall
    min_overlap: int = 1,
    diversify: bool = True,   # ✅ enable diversity selection by default
) -> Tuple[List[str], List[float]]:
    """
    Better gating to avoid mixed-doc contexts BUT keep "rich" technique passages:
    - Cleans passages (removes "3.1", [12], etc.)
    - Expands question (topic synonyms)
    - Base score = token overlap(question_tokens, passage_tokens)
    - Bonus score = technique-dense hints (few-shot/persona/metrics/etc.)
    - Select top_k with optional MMR-like diversity to avoid near-duplicates
    - Keep passages with overlap >= min_overlap when possible; else fallback to top scored
    """
    cleaned_passages = [_clean_passage(p) for p in (passages or [])]
    cleaned_passages = [p for p in cleaned_passages if p]

    if not cleaned_passages:
        return [], []

    expanded_q = _expand_question(question)

    scored: List[Tuple[str, float]] = []
    for p in cleaned_passages:
        base = _score_overlap(expanded_q, p)
        bonus = _technique_bonus(p)
        scored.append((p, base + bonus))

    scored.sort(key=lambda x: x[1], reverse=True)

    good = [(p, s) for (p, s) in scored if s >= float(min_overlap)]
    pool = good if len(good) >= 1 else scored

    chosen = _select_diverse_mmr(pool, top_k=top_k) if diversify else pool[:top_k]

    out_passages = [p for (p, _) in chosen]
    out_scores = [float(s) for (_, s) in chosen]
    return out_passages, out_scores
