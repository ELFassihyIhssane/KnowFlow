from __future__ import annotations

import json
import re
from typing import Dict, List, Any, Set, Optional, Tuple

from app.services.llm_client import call_llm


RELATIONS = ["is_a","instance_of","type_of","kind_of","part_of","has_part","component_of","has_component","subclass_of","superclass_of","variant_of","extends","derived_from","based_on","inspired_by","related_to","associated_with","linked_to","connected_to","correlated_with","depends_on","requires","prerequisite_for","condition_for","constrains","parameter","has_parameter","configured_by","controlled_by","governed_by","defined_by","described_by","formalized_by","modeled_by","represented_by","encoded_as","decoded_from","uses","used_for","applied_to","employed_in","leverages","exploits","incorporates","integrates","utilizes","relies_on","builds_on","enables","facilitates","supports","accelerates","improves","enhances","boosts","optimizes","stabilizes","regularizes","reduces","mitigates","limits","prevents","avoids","increases","amplifies","exacerbates","produces","generates","outputs","yields","results_in","leads_to","causes","induces","triggers","affects","influences","impacts","transforms","maps_to","converts_to","projects_to","measures","quantifies","estimates","approximates","evaluates","assesses","scores","computes","calculates","monitors","tracks","detects","predicts","infers","classifies","recognizes","identifies","segments","retrieves","generates_text","generates_image","generates_video","synthesizes","reconstructs","compresses","decompresses","encodes","decodes","trains","fine_tunes","optimizes_for","objective_is","loss_function","regularization_term","evaluation_metric","measured_by","evaluated_on","tested_on","validated_on","trained_on","benchmarked_on","compared_to","outperforms","underperforms","matches","exceeds","surpasses","falls_short_of","replaces","supersedes","obsoletes","alternatives_to","competes_with","complements","aggregates","combines","fuses","ensembles","distills","distilled_from","teacher_of","student_of","initializes","pretrains","posttrains","adapts","adapts_to","generalizes_to","fails_on","robust_to","sensitive_to","scales_with","bounded_by","limited_by","converges_to","diverges_from","stabilized_by","regulated_by","normalized_by","calibrated_by","scheduled_by","controlled_through","implemented_in","implemented_with","implemented_as","executed_on","runs_on","deployed_on","hosted_on","supported_by","maintained_by","released_as","version_of","updated_from","deprecated_by","compatible_with","incompatible_with","depends_temporally_on","precedes","follows","co_occurs_with","overlaps_with","shares_with","special_case_of","approximation_of","ablation_of","simplification_of","extension_of","composition_of","factor_of","invariant_of","property_of","characteristic_of","feature_of","indicator_of","proxy_for","signal_of","evidence_for","justifies","explains","motivates","addresses","solves","targets","focuses_on","applies_in","restricted_to","assumes","violates","satisfies","guarantees","bounds","upper_bounds","lower_bounds","tradeoff_with","balanced_against"]


STRICT_EVIDENCE_RELS = {
    "is_a",
    "part_of",
    "variant_of",
    "extends",
    "component_of",
    "depends_on",
    "parameter",
    "requires",
}

SOFT_EVIDENCE_RELS = set(RELATIONS) - STRICT_EVIDENCE_RELS

PROMPT_TEMPLATE = """
You are a knowledge-graph extraction engine.

You will receive:
- A USER QUESTION (what the user wants)
- PASSAGES (noisy, partial, not always perfect)

Your goal:
Build a clean knowledge graph that best answers the USER QUESTION.

Hard constraints:
- Use the PASSAGES only as evidence/context (no outside facts).
- Do NOT output junk tokens as concepts:
  section numbers (e.g., "3.1"), instruction/meta words ("knowledge graph", "relations"),
  citation markers ([12]), URLs, DOIs, author names, venues,
  and hyphen fragments like "post-" or "-based".

Concept rules:
- Concepts must be short noun phrases (1–6 words).
- Prefer scientific entities (methods/models/components/datasets/metrics) over generic words.
- Merge synonyms:
  "Large Language Model" and "LLM" -> one concept with aliases.
- Treat "post-training" as ONE phrase (e.g., "LLM post-training"), never as "post-".
- Include acronyms as aliases when present:
  "Trajectory Balance with Asynchrony (TBA)".

Edge rules:
- Use ONLY allowed relations (list below).
- Every edge MUST include an evidence snippet grounded in the passages (<= 25 words).
- Try to produce 6–12 edges if the passages support them.
- Center the graph on the USER QUESTION topic.
  Prefer edges touching the main topic concept.

Allowed relations:
{relations}

Output JSON ONLY (no markdown). Schema:
{{
  "concepts": [
    {{"label": "...", "type": "method|model|metric|task|dataset|concept|component|hyperparameter", "aliases": ["..."]}}
  ],
  "edges": [
    {{"source": "...", "target": "...", "relation": "...", "evidence": "..."}}
  ]
}}

USER QUESTION:
{question}

PASSAGES:
{passages}
""".strip()


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
    "require", "requires", "required",
    "measure", "measures", "measured",
    "evaluate", "evaluated", "evaluates",
    "produce", "produces", "produced",
    "aggregate", "aggregates", "aggregated",
    "extend", "extends", "extended",
}

_OPINION_WORDS = {
    "cute", "helpful", "amazing", "awesome", "great", "bad", "good", "nice",
    "better", "best", "worst", "fantastic", "terrible",
}

_GENERIC_CONCEPTS = {
    "learning", "training", "model", "method", "approach", "framework",
    "system", "algorithm", "experiment", "result", "analysis",
    "performance", "throughput", "scalability", "variance",
    "objective", "task",
}

_META_CONCEPTS = {
    "knowledge graph", "knowledge-graph", "graph", "relations", "relation",
    "concept", "concepts", "node", "nodes", "edge", "edges",
    "meaningful", "clear idea", "please", "extract",
}

_SECTION_ONLY_RE = re.compile(r"^\d+(?:\.\d+)+$")


def _parse_json_safe(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    text = raw.strip()
    text = re.sub(r"^```(json)?", "", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"```$", "", text).strip()

    try:
        return json.loads(text)
    except Exception:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(text[start:end + 1])
        except Exception:
            return {}
    return {}


def _tokenize(s: str) -> List[str]:
    s = (s or "").lower()
    s = _PUNCT_RE.sub(" ", s)
    return [t for t in _WORD_RE.findall(s) if t]


def _token_set(s: str) -> Set[str]:
    return set(_tokenize(s))


def _norm(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def _acronyms_from_label(label: str) -> Set[str]:
    out: Set[str] = set()
    s = label or ""
    for m in re.findall(r"\(([A-Za-z]{2,8})\)", s):
        out.add(m.lower())
    for tok in re.findall(r"\b[A-Z]{2,8}\b", s):
        out.add(tok.lower())
    return out


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


def _evidence_mentions_any(src: str, tgt: str, ev: str) -> bool:
    if not src or not tgt or not ev:
        return False

    ev_toks = {t for t in _token_set(ev) if len(t) > 2}
    if not ev_toks:
        return False

    src_toks = {t for t in _token_set(src) if len(t) > 2} | _acronyms_from_label(src)
    tgt_toks = {t for t in _token_set(tgt) if len(t) > 2} | _acronyms_from_label(tgt)
    return bool((src_toks & ev_toks) or (tgt_toks & ev_toks))


def _evidence_overlap_ok(src: str, tgt: str, ev: str, min_hits: int = 2) -> bool:
    if not src or not tgt or not ev:
        return False

    src_toks = {t for t in _token_set(src) if len(t) > 2} | _acronyms_from_label(src)
    tgt_toks = {t for t in _token_set(tgt) if len(t) > 2} | _acronyms_from_label(tgt)
    ev_toks = {t for t in _token_set(ev) if len(t) > 2}

    if not src_toks or not tgt_toks or not ev_toks:
        return False

    src_hits = src_toks & ev_toks
    tgt_hits = tgt_toks & ev_toks
    if len(src_hits) == 0 or len(tgt_hits) == 0:
        return False

    return (len(src_hits) + len(tgt_hits)) >= min_hits


def _is_hyphen_fragment(label: str) -> bool:
    s = (label or "").strip().lower()
    if re.fullmatch(r"[a-z]{2,}-", s):
        return True
    if re.fullmatch(r"-[a-z]{2,}", s):
        return True
    if len(s) <= 6 and ("-" in s) and len(_tokenize(s)) <= 1:
        return True
    return False


def _is_too_generic_concept(label: str) -> bool:
    toks = _tokenize(label)
    if not toks:
        return True

    low = _norm(label)

    if low in _META_CONCEPTS:
        return True
    if _SECTION_ONLY_RE.fullmatch(label.strip()):
        return True
    if _is_hyphen_fragment(label):
        return True

    if len(toks) == 1 and toks[0] in _GENERIC_CONCEPTS:
        return True
    if len(toks) == 1 and toks[0] in _OPINION_WORDS:
        return True
    if len(toks) == 1 and (len(toks[0]) <= 2 or toks[0].isdigit()):
        return True
    if re.fullmatch(r"\d+(\.\d+)+", label.strip()):
        return True

    return False


def _build_concept_index(concepts: List[Dict[str, Any]]) -> Tuple[Set[str], Dict[str, str], Dict[str, Set[str]]]:
    label_set_lower: Set[str] = set()
    alias_to_label: Dict[str, str] = {}
    label_to_tokens: Dict[str, Set[str]] = {}

    for c in concepts:
        lbl = str(c.get("label", "")).strip()
        if not lbl:
            continue
        lbl_low = lbl.lower()
        label_set_lower.add(lbl_low)

        toks = {t for t in _token_set(lbl) if len(t) > 2} | _acronyms_from_label(lbl)
        label_to_tokens[lbl_low] = toks

        for a in (c.get("aliases") or []):
            a = str(a).strip()
            if not a:
                continue
            alias_to_label[a.lower()] = lbl

        for ac in _acronyms_from_label(lbl):
            alias_to_label[ac.lower()] = lbl

    return label_set_lower, alias_to_label, label_to_tokens


def _resolve_endpoint(name: str, concepts: List[Dict[str, Any]]) -> Optional[str]:
    if not name:
        return None
    raw = name.strip()
    low = raw.lower()

    label_set_lower, alias_to_label, label_to_tokens = _build_concept_index(concepts)

    if low in label_set_lower:
        return next((c["label"] for c in concepts if c.get("label", "").strip().lower() == low), raw)

    if low in alias_to_label:
        return alias_to_label[low]

    name_toks = {t for t in _token_set(raw) if len(t) > 2} | _acronyms_from_label(raw)
    if not name_toks:
        return None

    best_label = None
    best_score = 0.0
    for lbl_low, toks in label_to_tokens.items():
        if not toks:
            continue
        inter = len(name_toks & toks)
        if inter <= 0:
            continue
        score = inter / max(1, len(name_toks))
        if score > best_score:
            best_score = score
            best_label = lbl_low

    if best_label and best_score >= 0.34:
        return next((c["label"] for c in concepts if c.get("label", "").strip().lower() == best_label), None)

    return None


def _topic_tokens(question: str) -> Set[str]:
    q = (question or "").strip()
    if not q:
        return set()
    toks = {t for t in _token_set(q) if len(t) > 2}
    for m in re.findall(r"\(([A-Za-z]{2,8})\)", q):
        toks.add(m.lower())
    return toks


def _pick_topic_concept(question: str, concepts: List[Dict[str, Any]]) -> Optional[str]:
    q_toks = _topic_tokens(question)
    if not q_toks or not concepts:
        return None

    best = None
    best_score = 0.0

    for c in concepts:
        lbl = str(c.get("label", "")).strip()
        if not lbl:
            continue
        ltoks = {t for t in _token_set(lbl) if len(t) > 2} | _acronyms_from_label(lbl)
        inter = len(q_toks & ltoks)
        if inter <= 0:
            continue
        score = inter / max(1, len(ltoks))
        if score > best_score:
            best_score = score
            best = lbl

    return best


def _evidence_mentions_label(label: str, evidence: str) -> bool:
    """
    True if evidence likely contains the label (or its acronyms / key tokens).
    This is a "safe" check: we only use it to decide whether to auto-add a missing endpoint.
    """
    if not label or not evidence:
        return False

    ev_low = evidence.lower()
    lbl_low = label.strip().lower()

    # exact/substring match helps with multiword phrases
    if len(lbl_low) >= 4 and lbl_low in ev_low:
        return True

    ev_toks = {t for t in _token_set(evidence) if len(t) > 2}
    if not ev_toks:
        return False

    lbl_toks = {t for t in _token_set(label) if len(t) > 2} | _acronyms_from_label(label)
    if not lbl_toks:
        return False

    # require at least one token hit
    return len(lbl_toks & ev_toks) >= 1


def extract_graph_with_gemini(
    question: str,
    passages: List[str],
    temperature: float = 0.6,
    timeout_s: int = 25,
    max_passage_chars: int = 1400,
) -> Dict[str, Any]:
    question = (question or "").strip()
    passages = [p.strip() for p in (passages or []) if (p or "").strip()]
    if not passages:
        return {"concepts": [], "edges": []}

    clipped: List[str] = []
    for p in passages:
        clipped.append(p[:max_passage_chars].rstrip() + ("..." if len(p) > max_passage_chars else ""))

    joined = "\n\n---\n\n".join(clipped)

    prompt = PROMPT_TEMPLATE.format(
        relations=", ".join(RELATIONS),
        question=question,
        passages=joined,
    )

    raw = call_llm(prompt, temperature=temperature, timeout_s=timeout_s)
    data = _parse_json_safe(raw)

    concepts = data.get("concepts", [])
    edges = data.get("edges", [])

    if not isinstance(concepts, list):
        concepts = []
    if not isinstance(edges, list):
        edges = []

    out_concepts: List[Dict[str, Any]] = []
    seen = set()

    for c in concepts[:160]:
        if not isinstance(c, dict):
            continue
        label = str(c.get("label", "")).strip()
        ctype = str(c.get("type", "concept")).strip() or "concept"

        aliases = c.get("aliases", [])
        if not isinstance(aliases, list):
            aliases = []
        aliases = [str(a).strip() for a in aliases if str(a).strip()]

        if not label:
            continue
        if _is_too_generic_concept(label):
            continue

        key = label.lower()
        if key in seen:
            continue
        seen.add(key)

        for ac in _acronyms_from_label(label):
            if ac and ac.lower() not in [a.lower() for a in aliases]:
                aliases.append(ac)

        out_concepts.append({"label": label, "type": ctype, "aliases": aliases[:8]})

    out_edges: List[Dict[str, str]] = []
    dedup = set()

    # ✅ helper: add missing endpoints as concepts (MVP-safe)
    def _ensure_concept(label: str) -> str:
        lbl = (label or "").strip()
        if not lbl:
            return lbl
        low = lbl.lower()
        if any((c.get("label", "").strip().lower() == low) for c in out_concepts if isinstance(c, dict)):
            return next((c.get("label") for c in out_concepts if c.get("label", "").strip().lower() == low), lbl)
        # add minimal node; do NOT block edges
        out_concepts.append({"label": lbl, "type": "concept", "aliases": []})
        return lbl

    for e in edges[:260]:
        if not isinstance(e, dict):
            continue

        src_raw = str(e.get("source", "")).strip()
        tgt_raw = str(e.get("target", "")).strip()
        rel = str(e.get("relation", "")).strip()
        ev = str(e.get("evidence", "")).strip()

        if not src_raw or not tgt_raw or not rel:
            continue
        if rel not in RELATIONS:
            continue

        if not ev:
            continue
        if _is_title_like_evidence(ev):
            continue

        # Try resolve against extracted concepts
        src = _resolve_endpoint(src_raw, out_concepts)
        tgt = _resolve_endpoint(tgt_raw, out_concepts)

        # ✅ Fix: if resolution fails BUT evidence contains endpoint -> auto-add endpoint
        if not src and _evidence_mentions_label(src_raw, ev):
            src = _ensure_concept(src_raw)
        if not tgt and _evidence_mentions_label(tgt_raw, ev):
            tgt = _ensure_concept(tgt_raw)

        # If still missing, drop (likely hallucination)
        if not src or not tgt:
            continue

        if rel in STRICT_EVIDENCE_RELS:
            if not _evidence_overlap_ok(src, tgt, ev, min_hits=2):
                continue
        else:
            if not _evidence_mentions_any(src, tgt, ev):
                continue

        key = (src.lower(), tgt.lower(), rel.lower())
        if key in dedup:
            continue
        dedup.add(key)

        out_edges.append({"source": src, "target": tgt, "relation": rel, "evidence": ev})

    topic = _pick_topic_concept(question, out_concepts)
    if topic and out_edges:
        touching = [ed for ed in out_edges if ed["source"] == topic or ed["target"] == topic]
        others = [ed for ed in out_edges if ed not in touching]
        out_edges = touching + others

    return {"concepts": out_concepts[:70], "edges": out_edges[:160]}
