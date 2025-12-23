from __future__ import annotations

import re
from typing import Dict, Any, List, Tuple, Set


VENUE_PATTERNS = [
    r"\bneurips\b", r"\bicra\b", r"\bnaacl\b", r"\bicml\b", r"\bcvpr\b", r"\beccv\b",
    r"\bacl\b", r"\bemnlp\b", r"\bijcai\b", r"\bkdd\b", r"\bnips\b",
    r"\bproceedings\b", r"\bconference\b", r"\bjournal of\b",
]

DOI_PATTERN = r"\b10\.\d{4,9}/\S+\b"
URL_PATTERN = r"https?://\S+"
CIT_PATTERN = r"\[\s*\d+(?:\s*,\s*\d+)*\s*\]"
SECTION_PATTERN = r"^\d+(\.\d+)+$"

_WORD_RE = re.compile(r"[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*")
_PUNCT_RE = re.compile(r"[^a-z0-9\.\-\s_/]+", re.IGNORECASE)

_COMMON_VERBS = {
    "is", "are", "was", "were",
    "use", "uses", "using",
    "enable", "enables", "enabled",
    "improve", "improves", "improved",
    "reduce", "reduces", "reduced",
    "increase", "increases", "increased",
    "replace", "replaces", "replaced",
    "compare", "compares", "compared",
    "outperform", "outperforms", "outperformed",
    "depend", "depends", "depended",
    "apply", "applies", "applied",
    "decouple", "decouples", "decoupled",
    "stabilize", "stabilizes", "stabilized",
    "require", "requires", "required",
    "measure", "measures", "measured",
    "evaluate", "evaluates", "evaluated",
    "produce", "produces", "produced",
    "aggregate", "aggregates", "aggregated",
    "extend", "extends", "extended",
}

GENERIC_TOKENS = {
    "learning", "training", "model", "method", "approach", "framework",
    "system", "algorithm", "experiment", "result", "analysis",
    "performance", "throughput", "scalability", "variance",
    "exploration", "policy", "objective", "task",
}

OPINION_TOKENS = {
    "cute", "helpful", "amazing", "awesome", "great", "bad", "good", "nice",
    "better", "best", "worst", "fantastic", "terrible",
}

INSTRUCTION_TOKENS = {
    "extract", "please", "pleaze", "concept", "concepts", "relation", "relations",
    "knowledge", "graph", "meaningful", "clear", "idea", "put", "make", "give",
    "generate", "build", "need", "want", "related", "topic", "about",
}

STRICT_EVIDENCE_RELS = {
    "is_a",
    "part_of",
    "component_of",
    "variant_of",
    "extends",
    "depends_on",
    "requires",
    "parameter",
}

SOFT_EVIDENCE_RELS = {
    "used_for",
    "applied_to",
    "evaluated_on",
    "outperforms",
    "compares_to",
    "improves",
    "reduces",
    "increases",
    "produces",
    "measures",
    "replaces",
    "aggregates",
}


def _tokenize(s: str) -> List[str]:
    s = (s or "").lower()
    s = _PUNCT_RE.sub(" ", s)
    return [t for t in _WORD_RE.findall(s) if t]


def _token_set(s: str) -> Set[str]:
    return set(_tokenize(s))


def _is_noise_label(label: str) -> bool:
    if not label:
        return True
    s = label.strip()
    low = s.lower()

    if re.search(URL_PATTERN, s):
        return True
    if re.search(DOI_PATTERN, s):
        return True
    if re.search(CIT_PATTERN, s):
        return True
    if re.fullmatch(SECTION_PATTERN, s):
        return True
    for pat in VENUE_PATTERNS:
        if re.search(pat, low):
            return True
    return False


def _is_too_generic(label: str) -> bool:
    toks = _tokenize(label)
    if not toks:
        return True
    if len(toks) == 1 and toks[0] in GENERIC_TOKENS:
        return True
    if len(toks) == 1 and toks[0] in OPINION_TOKENS:
        return True
    if len(toks) == 1 and len(toks[0]) <= 3 and not re.search(r"[A-Z]", label):
        return True
    return False


def _is_title_like_evidence(ev: str) -> bool:
    if not ev:
        return True
    raw = ev.strip()
    toks = _tokenize(raw)
    if len(toks) < 4:
        return True
    if not any(v in toks for v in _COMMON_VERBS):
        return True
    if ":" in raw and len(toks) >= 8:
        return True
    return False


def _evidence_overlap_ok(src: str, tgt: str, ev: str, min_hits: int = 2) -> bool:
    if not src or not tgt or not ev:
        return False

    src_toks = {t for t in _token_set(src) if len(t) > 2}
    tgt_toks = {t for t in _token_set(tgt) if len(t) > 2}
    ev_toks = {t for t in _token_set(ev) if len(t) > 2}

    if not src_toks or not tgt_toks or not ev_toks:
        return False

    src_hits = src_toks & ev_toks
    tgt_hits = tgt_toks & ev_toks
    if len(src_hits) == 0 or len(tgt_hits) == 0:
        return False

    return (len(src_hits) + len(tgt_hits)) >= min_hits


def _evidence_mentions_any(src: str, tgt: str, ev: str) -> bool:
    if not src or not tgt or not ev:
        return False

    ev_toks = {t for t in _token_set(ev) if len(t) > 2}
    if not ev_toks:
        return False

    src_toks = {t for t in _token_set(src) if len(t) > 2}
    tgt_toks = {t for t in _token_set(tgt) if len(t) > 2}

    return bool((src_toks & ev_toks) or (tgt_toks & ev_toks))


def _topic_tokens(question: str) -> Set[str]:
    q = (question or "").strip()
    if not q:
        return set()

    toks: Set[str] = set()

    for m in re.findall(r"\(([A-Za-z]{2,8})\)", q):
        toks.add(m.lower())

    caps = re.findall(r"\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,5}\b", q)
    for phrase in caps:
        for t in _token_set(phrase):
            if len(t) > 2:
                toks.add(t)

    for t in _token_set(q):
        if len(t) <= 2:
            continue
        if t in INSTRUCTION_TOKENS:
            continue
        toks.add(t)

    return toks


def _is_instruction_heavy(question: str) -> bool:
    q_toks = _token_set(question)
    if not q_toks:
        return True
    instr = len([t for t in q_toks if t in INSTRUCTION_TOKENS])
    return instr / max(1, len(q_toks)) >= 0.45


def assess_graph_quality(
    graph: Dict[str, Any],
    min_concepts: int = 6,
    min_edges: int = 1,
    require_evidence: bool = True,
    max_generic_ratio: float = 0.45,
    min_relation_diversity: int = 1,
    max_part_of_ratio: float = 0.55,
    min_question_alignment_hits: int = 1,
    question: str | None = None,
    strict_question_alignment: bool = False,
) -> Tuple[bool, List[str]]:
    issues: List[str] = []

    concepts = graph.get("concepts", [])
    edges = graph.get("edges", [])

    if not isinstance(concepts, list):
        concepts = []
        issues.append("concepts is not a list")
    if not isinstance(edges, list):
        edges = []
        issues.append("edges is not a list")

    if len(concepts) < min_concepts:
        issues.append(f"too few concepts ({len(concepts)} < {min_concepts})")

    labels: List[str] = []
    noise: List[str] = []
    generic: List[str] = []

    for c in concepts:
        if not isinstance(c, dict):
            continue
        label = str(c.get("label", "")).strip()
        if not label:
            continue
        labels.append(label)

        if _is_noise_label(label):
            noise.append(label)
        if _is_too_generic(label):
            generic.append(label)

    if noise:
        issues.append(f"noise concepts detected: {noise[:6]}")

    if labels:
        gen_ratio = len(generic) / max(1, len(labels))
        if gen_ratio > max_generic_ratio:
            issues.append(f"too many generic concepts ({len(generic)}/{len(labels)} = {gen_ratio:.2f})")

    if len(edges) < min_edges:
        issues.append(f"too few edges ({len(edges)} < {min_edges})")

    label_set = {l.strip().lower() for l in labels if l.strip()}

    bad_edges = 0
    missing_ev = 0
    dangling = 0
    title_like_ev = 0
    weak_overlap = 0

    rel_counts: Dict[str, int] = {}

    for e in edges:
        if not isinstance(e, dict):
            bad_edges += 1
            continue

        src = str(e.get("source", "")).strip()
        tgt = str(e.get("target", "")).strip()
        rel = str(e.get("relation", "")).strip()
        ev = str(e.get("evidence", "")).strip()

        if not src or not tgt or not rel:
            bad_edges += 1
            continue

        rel_counts[rel] = rel_counts.get(rel, 0) + 1

        if require_evidence:
            if not ev:
                missing_ev += 1
            else:
                if _is_title_like_evidence(ev):
                    title_like_ev += 1
                else:
                    if rel in STRICT_EVIDENCE_RELS:
                        if not _evidence_overlap_ok(src, tgt, ev):
                            weak_overlap += 1
                    else:
                        if not _evidence_mentions_any(src, tgt, ev):
                            weak_overlap += 1

        if src.lower() not in label_set or tgt.lower() not in label_set:
            dangling += 1

        if rel == "evaluated_on" and _is_noise_label(tgt):
            bad_edges += 1

    if bad_edges > 0:
        issues.append(f"bad edges: {bad_edges}")
    if require_evidence and missing_ev > 0:
        issues.append(f"edges missing evidence: {missing_ev}")
    if dangling > 0:
        issues.append(f"dangling edges (source/target not in concepts): {dangling}")
    if require_evidence and title_like_ev > 0:
        issues.append(f"title-like evidence edges: {title_like_ev}")

    total_edges = len(edges)
    if require_evidence and weak_overlap > 0:
        ratio = weak_overlap / max(1, total_edges)
        if total_edges >= 4 and ratio >= 0.5:
            issues.append(f"weak evidence overlap edges: {weak_overlap} (ratio={ratio:.2f})")
        elif total_edges < 4 and weak_overlap >= 2:
            issues.append(f"weak evidence overlap edges: {weak_overlap} (small-graph)")
        else:
            issues.append(f"weak evidence overlap edges (warning): {weak_overlap}/{total_edges}")

    if rel_counts:
        total = sum(rel_counts.values())
        if total >= 4:
            if len(rel_counts.keys()) < min_relation_diversity:
                issues.append(f"low relation diversity ({len(rel_counts.keys())} < {min_relation_diversity})")

            part_of = rel_counts.get("part_of", 0)
            part_ratio = part_of / max(1, total)
            if part_ratio > max_part_of_ratio:
                issues.append(f"too many part_of edges ({part_of}/{total} = {part_ratio:.2f})")

    if question and labels:
        q = question.strip()
        if q:
            instruction_heavy = _is_instruction_heavy(q)
            q_toks = _topic_tokens(q)

            if q_toks:
                hits = 0
                for lbl in labels:
                    l_toks = {t for t in _token_set(lbl) if len(t) > 2}
                    if (q_toks & l_toks):
                        hits += 1

                if hits < min_question_alignment_hits:
                    issues.append(f"low question alignment (only {hits} concepts overlap topic tokens)")
                    if strict_question_alignment and not instruction_heavy:
                        pass

    if strict_question_alignment:
        ok = len(issues) == 0
    else:
        fatal_issues: List[str] = []
        for it in issues:
            if it.startswith("low question alignment"):
                continue
            if it.startswith("weak evidence overlap edges (warning)"):
                continue
            fatal_issues.append(it)
        ok = len(fatal_issues) == 0

    return ok, issues
